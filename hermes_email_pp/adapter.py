"""Secure IMAP/SMTP transport for the Email++ Hermes platform."""

from __future__ import annotations

import asyncio
import email
import imaplib
import logging
import mimetypes
import re
import smtplib
import ssl
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from email.headerregistry import Address
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formatdate, parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Any

from gateway.config import Platform  # type: ignore[import-not-found]
from gateway.platforms.base import (  # type: ignore[import-not-found]
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
    cache_audio_from_bytes,
    cache_document_from_bytes,
    cache_image_from_bytes,
    cache_video_from_bytes,
    validate_inbound_media_size,
)

from .config import environment_settings, process_history_window
from .forwarding import (
    ForwardedMessage,
    hermes_prompt,
    html_to_text,
    is_suspected_forward,
    parse_forward,
)
from .rendering import quote_html, quote_plain, render_markdown
from .threading import EmailThreadRouter, ThreadRoute

_AUTOMATED = ("noreply", "no-reply", "mailer-daemon", "postmaster", "bounce")
_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MESSAGE_ID = re.compile(r"<[^\s<>@]+@[^\s<>@]+>")
_MESSAGE_IDS = re.compile(r"<[^\s<>@]+@[^\s<>@]+>(?:\s+<[^\s<>@]+@[^\s<>@]+>)*")
_INTERNALDATE = re.compile(rb'INTERNALDATE "([^"]+)"')
_POLL_BATCH_SIZE = 25
logger = logging.getLogger(__name__)


@dataclass
class _MailboxState:
    """State retained across automatic reconnects in one gateway process."""

    uidvalidity: bytes | None
    baseline_uid: int
    seen: set[bytes]


def _decode(value: str) -> str:
    """Decode an RFC 2047 header without letting a bad charset abort a poll."""
    decoded: list[str] = []
    for part, charset in decode_header(value):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            except LookupError:
                decoded.append(part.decode("utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _address(value: str) -> str:
    """Return a normalized RFC address or an empty value for unsafe input."""
    _, address = parseaddr(value)
    address = address.strip().lower()
    return address if "@" in address and " " not in address else ""


def _message_ids(value: object) -> list[str]:
    """Return valid Message-IDs without permitting header injection."""
    if not isinstance(value, str) or "\r" in value or "\n" in value:
        return []
    return _MESSAGE_ID.findall(value) if _MESSAGE_IDS.fullmatch(value.strip()) else []


def _display_name(value: str) -> str:
    """Extract a header-safe display name from a decoded mailbox header."""
    name, _ = parseaddr(_decode(value))
    return name.replace("\r", "").replace("\n", "").strip()


class EmailPPAdapter(BasePlatformAdapter):
    """Poll a TLS mailbox and deliver only explicitly routed email replies."""

    _mailbox_states: dict[tuple[str, str], _MailboxState] = {}

    def __init__(self, config: Any) -> None:
        super().__init__(config, Platform("email_pp"))
        extra = getattr(config, "extra", {}) or {}
        settings = environment_settings()
        self._address = self._setting(settings, extra, "EMAIL_PP_ADDRESS", "address")
        self._password = self._setting(settings, extra, "EMAIL_PP_PASSWORD", "password")
        self._imap_host = self._setting(
            settings, extra, "EMAIL_PP_IMAP_HOST", "imap_host"
        )
        self._smtp_host = self._setting(
            settings, extra, "EMAIL_PP_SMTP_HOST", "smtp_host"
        )
        self._imap_port = self._integer(
            settings, extra, "EMAIL_PP_IMAP_PORT", "imap_port", 993
        )
        self._smtp_port = self._integer(
            settings, extra, "EMAIL_PP_SMTP_PORT", "smtp_port", 587
        )
        self._poll_interval = self._integer(
            settings, extra, "EMAIL_PP_POLL_INTERVAL", "poll_interval", 15
        )
        self._mailbox = (
            self._setting(settings, extra, "EMAIL_PP_MAILBOX", "mailbox") or "INBOX"
        )
        allowed_users = self._setting(
            settings, extra, "EMAIL_PP_ALLOWED_USERS", "allowed_users"
        )
        self._allowed = {
            value.strip().lower()
            for value in allowed_users.split(",")
            if _address(value)
        }
        self._allow_all = self._setting(
            settings, extra, "EMAIL_PP_ALLOW_ALL_USERS", "allow_all_users"
        ).lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._require_auth = settings.get(
            "EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER",
            str(extra.get("require_authenticated_sender", True)),
        ).lower() not in {"0", "false", "no", "off"}
        self._authserv_id = self._setting(
            settings, extra, "EMAIL_PP_AUTHSERV_ID", "authserv_id"
        )
        self._quote_mode = self._parse_quote_mode(settings, extra)
        self._process_history_window = process_history_window(
            self._setting(
                settings,
                extra,
                "EMAIL_PP_PROCESS_HISTORY_WINDOW",
                "process_history_window",
            )
        )
        self._seen: set[bytes] = set()
        self._baseline_uid = 0
        self._uidvalidity: bytes | None = None
        self._history_cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=max(0, self._process_history_window)
        )
        self._poll_task: asyncio.Task[None] | None = None
        self._routes: dict[tuple[str, str], ThreadRoute] = {}
        self._router = EmailThreadRouter()

    @staticmethod
    def _setting(settings: dict[str, str], extra: Any, env: str, key: str) -> str:
        value = settings.get(env) or extra.get(key, "")
        if isinstance(value, (list, tuple, set)):
            value = ",".join(str(item) for item in value)
        return str(value).strip()

    @classmethod
    def _integer(
        cls, settings: dict[str, str], extra: Any, env: str, key: str, default: int
    ) -> int:
        try:
            return int(cls._setting(settings, extra, env, key))
        except ValueError:
            return default

    @classmethod
    def _parse_quote_mode(cls, settings: dict[str, str], extra: Any) -> str:
        mode = cls._setting(settings, extra, "EMAIL_PP_QUOTE_MODE", "quote_mode")
        mode = mode.lower() or "always"
        if mode not in {"always", "forwarded", "never"}:
            raise ValueError(
                "EMAIL_PP_QUOTE_MODE must be one of: always, forwarded, never"
            )
        return mode

    async def connect(self, *, is_reconnect: bool = False) -> bool:
        """Validate both TLS transports and begin asynchronous mailbox polling."""
        if not all((self._address, self._password, self._imap_host, self._smtp_host)):
            logger.warning(
                "Email++ connection rejected because required settings are missing"
            )
            return False
        try:
            logger.info("Email++ IMAP connection starting")
            if not self._acquire_platform_lock(
                "email_pp", self._address, "Email++ mailbox"
            ):
                return False
            await asyncio.to_thread(self._baseline_mailbox, is_reconnect)
            await asyncio.to_thread(self._probe_smtp)
        except (OSError, imaplib.IMAP4.error, smtplib.SMTPException):
            logger.warning("Email++ connection validation failed")
            self._release_platform_lock()
            return False
        self._mark_connected()
        self._poll_task = asyncio.create_task(self._poll_loop())
        logger.info("Email++ IMAP polling started")
        return True

    async def disconnect(self) -> None:
        """Stop polling without leaving a running task behind."""
        self._running = False
        if self._poll_task is not None:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None
        self._release_platform_lock()
        self._mark_disconnected()
        logger.info("Email++ IMAP polling stopped")

    def _baseline_mailbox(self, is_reconnect: bool) -> None:
        imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, timeout=30)
        try:
            imap.login(self._address, self._password)
            uidvalidity = self._select_mailbox(imap)
            cached = self._mailbox_states.get(self._mailbox_key)
            if (
                is_reconnect
                and cached is not None
                and cached.uidvalidity == uidvalidity
            ):
                self._restore_mailbox_state(cached)
                logger.info("Email++ IMAP reconnect restored mailbox state")
                return
            if is_reconnect and cached is not None:
                logger.warning(
                    "Email++ IMAP UIDVALIDITY changed; applying cold-start recovery"
                )
            self._start_cold_mailbox(imap, uidvalidity)
        finally:
            self._close_imap(imap)

    @property
    def _mailbox_key(self) -> tuple[str, str]:
        return (self._address.lower(), self._mailbox)

    def _restore_mailbox_state(self, state: _MailboxState) -> None:
        self._uidvalidity = state.uidvalidity
        self._baseline_uid = state.baseline_uid
        self._seen = set(state.seen)

    def _save_mailbox_state(self) -> None:
        self._mailbox_states[self._mailbox_key] = _MailboxState(
            self._uidvalidity, self._baseline_uid, set(self._seen)
        )

    def _start_cold_mailbox(
        self, imap: imaplib.IMAP4, uidvalidity: bytes | None
    ) -> None:
        all_uids = self._search_uids(imap, "ALL")
        valid_uids = [
            value for uid in all_uids if (value := self._uid_number(uid)) is not None
        ]
        self._uidvalidity = uidvalidity
        self._baseline_uid = max(valid_uids, default=0)
        self._seen = set()
        self._history_cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=max(0, self._process_history_window)
        )
        self._save_mailbox_state()
        logger.info(
            "Email++ IMAP cold-start state recorded (history_window=%d)",
            self._process_history_window,
        )

    @staticmethod
    def _uid_number(uid: bytes) -> int | None:
        try:
            value = int(uid)
        except ValueError:
            logger.warning("Email++ IMAP ignored malformed UID response")
            return None
        return value if value >= 0 else None

    def _select_mailbox(self, imap: imaplib.IMAP4) -> bytes | None:
        status, _ = imap.select(self._mailbox)
        if status != "OK":
            logger.warning("Email++ IMAP mailbox selection failed")
            raise imaplib.IMAP4.error("IMAP mailbox selection failed")
        response = imap.response("UIDVALIDITY")
        if not isinstance(response, tuple) or len(response) != 2:
            logger.warning("Email++ IMAP returned malformed UIDVALIDITY response")
            return None
        _, values = response
        if not values or not isinstance(values[0], bytes):
            return None
        return values[0]

    @staticmethod
    def _search_uids(imap: imaplib.IMAP4, criteria: str) -> list[bytes]:
        status, data = imap.uid("search", None, criteria)  # type: ignore[arg-type]
        if status != "OK":
            logger.warning("Email++ IMAP UID search failed (criteria=%s)", criteria)
            raise imaplib.IMAP4.error("IMAP UID search failed")
        if not isinstance(data, (list, tuple)) or not data:
            logger.warning("Email++ IMAP returned malformed UID search response")
            raise imaplib.IMAP4.error("IMAP UID search returned malformed data")
        if not isinstance(data[0], bytes):
            logger.warning("Email++ IMAP returned malformed UID search data")
            raise imaplib.IMAP4.error("IMAP UID search returned malformed data")
        return data[0].split()

    @staticmethod
    def _close_imap(imap: imaplib.IMAP4) -> None:
        try:
            imap.logout()
        except Exception:
            try:
                imap.shutdown()
            except Exception:
                pass

    def _smtp(self) -> smtplib.SMTP:
        context = ssl.create_default_context()
        if self._smtp_port == 465:
            return smtplib.SMTP_SSL(
                self._smtp_host, self._smtp_port, timeout=30, context=context
            )
        smtp = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30)
        smtp.starttls(context=context)
        return smtp

    def _probe_smtp(self) -> None:
        smtp = self._smtp()
        try:
            smtp.login(self._address, self._password)
        finally:
            smtp.quit()

    # Gateway lifecycle drives this loop; its worker calls are covered below.
    async def _poll_loop(self) -> None:  # pragma: no cover
        while self._running:
            try:
                messages = await asyncio.to_thread(self._fetch_unseen)
                logger.debug("Email++ IMAP poll fetched batch_size=%d", len(messages))
                for raw in messages:
                    try:
                        await self._dispatch(raw)
                    except Exception:
                        logger.warning("Email++ IMAP message dispatch failed")
                        continue
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.warning("Email++ IMAP polling failed")
                self._set_fatal_error(
                    "poll_failed", "IMAP polling failed", retryable=True
                )
                await self._notify_fatal_error()
                return
            await asyncio.sleep(max(1, self._poll_interval))

    def _fetch_unseen(self) -> list[bytes]:
        imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, timeout=30)
        messages: list[bytes] = []
        try:
            imap.login(self._address, self._password)
            uidvalidity = self._select_mailbox(imap)
            if uidvalidity != self._uidvalidity:
                logger.warning("Email++ IMAP UIDVALIDITY changed during polling")
                self._start_cold_mailbox(imap, uidvalidity)
            attempts = 0
            for uid in sorted(
                self._search_uids(imap, "UNSEEN"), key=self._uid_sort_key
            ):
                if uid in self._seen:
                    continue
                uid_number = self._uid_number(uid)
                if uid_number is None:
                    continue
                if (
                    uid_number <= self._baseline_uid
                    and self._process_history_window == 0
                ):
                    continue
                if attempts >= _POLL_BATCH_SIZE:
                    break
                attempts += 1
                fetched = self._fetch_message(imap, uid)
                if fetched is None:
                    continue
                raw, internaldate = fetched
                if (
                    uid_number <= self._baseline_uid
                    and self._process_history_window > 0
                    and (internaldate is None or internaldate <= self._history_cutoff)
                ):
                    if internaldate is None:
                        logger.warning(
                            "Email++ IMAP skipped unread history with malformed "
                            "INTERNALDATE"
                        )
                    self._seen.add(uid)
                    continue
                self._seen.add(uid)
                messages.append(raw)
            self._trim_seen()
            self._save_mailbox_state()
            if attempts:
                logger.info(
                    "Email++ IMAP completed poll batch (fetched=%d, attempted=%d)",
                    len(messages),
                    attempts,
                )
            return messages
        finally:
            self._close_imap(imap)

    @staticmethod
    def _uid_sort_key(uid: bytes) -> int:
        return int(uid) if uid.isdigit() else -1

    @staticmethod
    def _fetch_message(
        imap: imaplib.IMAP4, uid: bytes
    ) -> tuple[bytes, datetime | None] | None:
        status, data = imap.uid("fetch", uid.decode("ascii"), "(RFC822 INTERNALDATE)")
        if status != "OK" or not isinstance(data, (list, tuple)) or not data:
            logger.warning("Email++ IMAP message fetch failed")
            return None
        raw: bytes | None = None
        metadata: list[bytes] = []
        for index, item in enumerate(data):
            if not isinstance(item, tuple) or len(item) != 2:
                continue
            descriptor, literal = item
            if (
                not isinstance(descriptor, bytes)
                or not isinstance(literal, bytes)
                or b"RFC822" not in descriptor
            ):
                continue
            raw = literal
            metadata.append(descriptor)
            # imaplib appends protocol attributes after an RFC822 literal.
            # Only inspect those attributes, never bytes from the message body.
            metadata.extend(
                item for item in data[index + 1 :] if isinstance(item, bytes)
            )
            break
        if raw is None:
            logger.warning("Email++ IMAP returned malformed message fetch data")
            return None
        match = _INTERNALDATE.search(b" ".join(metadata))
        if match is None:
            return raw, None
        try:
            internaldate = parsedate_to_datetime(match.group(1).decode("ascii"))
        except (TypeError, ValueError, UnicodeDecodeError):
            return raw, None
        if internaldate.tzinfo is None:
            return raw, None
        return raw, internaldate.astimezone(timezone.utc)

    def _trim_seen(self) -> None:
        if len(self._seen) > 2000:
            self._seen = set(sorted(self._seen, key=int)[-1000:])

    async def _dispatch(self, raw: bytes) -> None:
        message = email.message_from_bytes(raw)
        sender = _address(message.get("From", ""))
        if not self._permitted(sender, message):
            return
        route = self._router.resolve(
            sender,
            message_id=message.get("Message-ID"),
            references=message.get("References"),
            in_reply_to=message.get("In-Reply-To"),
        )
        message_id = message.get("Message-ID", "")
        if message_id:
            self._routes[(sender, message_id)] = route
        text, urls, types, message_type = self._content(message)
        alternatives = self._text_alternatives(message)
        subject = _decode(message.get("Subject", ""))
        message_ids = _message_ids(message_id)
        references = _message_ids(message.get("References", ""))
        if message_ids:
            references.append(message_ids[0])
        forward = self._forward(alternatives)
        if forward is None and is_suspected_forward(subject, alternatives):
            self._router.update_context(
                route,
                delivery_context={
                    "display_name": _display_name(message.get("From", sender)),
                    "subject": subject,
                },
                quote_source={"body": "", "is_forwarded": "false"},
                draft_context={"is_forwarded": "false", "draft_sent": "true"},
            )
            await self._send_unsafe_forward_notice(route, message_id)
            return
        self._router.update_context(
            route,
            delivery_context={
                "display_name": _display_name(message.get("From", sender)),
                "subject": subject,
            },
            quote_source={
                "body": (forward.quote if forward else text)[:100_000],
                "sender": forward.original_sender if forward else sender,
                "references": " ".join(dict.fromkeys(references)),
                "is_forwarded": str(bool(forward)).lower(),
            },
            draft_context=self._draft_context(forward),
        )
        source = self.build_source(
            chat_id=route.chat_id,
            chat_name=_decode(message.get("From", sender)),
            chat_type="dm",
            user_id=sender,
            user_name=sender,
            thread_id=route.thread_id,
            message_id=message_id or None,
        )
        await self.handle_message(
            MessageEvent(
                text=hermes_prompt(forward) if forward else text or "(empty email)",
                message_type=message_type,
                source=source,
                message_id=message_id or None,
                reply_to_message_id=message.get("In-Reply-To") or None,
                media_urls=urls,
                media_types=types,
            )
        )

    @staticmethod
    def _text_alternatives(message: Any) -> list[str]:
        alternatives: list[str] = []
        for part in message.walk() if message.is_multipart() else [message]:
            if "attachment" in str(part.get("Content-Disposition", "")):
                continue
            content_type = part.get_content_type()
            if content_type not in {"text/plain", "text/html"}:
                continue
            payload = part.get_payload(decode=True) or b""
            body = payload.decode(
                part.get_content_charset() or "utf-8", errors="replace"
            )
            alternatives.append(
                html_to_text(body) if content_type == "text/html" else body
            )
        return alternatives

    @staticmethod
    def _forward(alternatives: list[str]) -> ForwardedMessage | None:
        return next(
            (forward for body in alternatives if (forward := parse_forward(body))), None
        )

    @staticmethod
    def _draft_context(forward: ForwardedMessage | None) -> dict[str, str]:
        if forward is None:
            return {"is_forwarded": "false", "draft_sent": "true"}
        return {
            "is_forwarded": "true",
            "draft_sent": "false",
            "task_prompt": forward.task_prompt[:100_000],
            "original_sender": forward.original_sender,
            "original_date": forward.original_date,
            "original_to": forward.original_to,
            "original_cc": forward.original_cc,
            "original_subject": forward.original_subject,
            "original_body": forward.original_body[:100_000],
        }

    async def _send_unsafe_forward_notice(
        self, route: ThreadRoute, message_id: str
    ) -> None:
        reply_ids = _message_ids(message_id)
        if len(reply_ids) != 1:
            return
        content = (
            "I could not safely identify the boundary between your task and "
            "the forwarded message, so no review draft was created. Please "
            "resend it with a separate task prompt followed by a complete "
            "Gmail or Outlook inline forward."
        )
        sent = await asyncio.to_thread(
            self._send_email, route, content, reply_ids[0], None, None
        )
        self._routes[(route.chat_id, sent)] = route
        self._router.record_outbound(route, sent)

    def _permitted(self, sender: str, message: Any) -> bool:
        if (
            not sender
            or sender == self._address.lower()
            or any(x in sender for x in _AUTOMATED)
        ):
            logger.debug(
                "Email++ rejected inbound message: invalid or automated sender"
            )
            return False
        if not self._allow_all and sender not in self._allowed:
            logger.debug("Email++ rejected inbound message: sender is not allowlisted")
            return False
        if self._allow_all or not self._require_auth:
            return True
        headers = message.get_all("Authentication-Results") or []
        for header in headers:
            normalized = " ".join(header.split())
            if self._authserv_id and not normalized.lower().startswith(
                self._authserv_id.lower()
            ):
                continue
            if re.search(r"\bdmarc\s*=\s*pass\b", normalized, re.I):
                return True
        logger.debug("Email++ rejected inbound message: sender authentication failed")
        return False

    def _content(self, message: Any) -> tuple[str, list[str], list[str], Any]:
        text = ""
        html = ""
        urls: list[str] = []
        types: list[str] = []
        message_type = MessageType.TEXT
        for part in message.walk() if message.is_multipart() else [message]:
            payload = part.get_payload(decode=True) or b""
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                text = payload.decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
            elif content_type == "text/html" and "attachment" not in disposition:
                html = re.sub(r"<[^>]+>", "", payload.decode("utf-8", errors="replace"))
            elif "attachment" in disposition or part.get_filename():
                path, attachment_type = self._cache_attachment(
                    payload, content_type, part.get_filename()
                )
                urls.append(path)
                types.append(content_type)
                message_type = attachment_type
        return text or html, urls, types, message_type

    @staticmethod
    def _cache_attachment(
        payload: bytes, content_type: str, filename: str | None
    ) -> tuple[str, Any]:
        """Store inbound media in Hermes' bounded profile cache."""
        safe_name = filename or "attachment"
        suffix = Path(safe_name).suffix or ".bin"
        validate_inbound_media_size(len(payload), media_type="email attachment")
        if content_type in _IMAGE_TYPES:
            try:
                return cache_image_from_bytes(payload, suffix), MessageType.PHOTO
            except ValueError:
                # A false image claim remains available as a document.
                return (
                    cache_document_from_bytes(payload, safe_name),
                    MessageType.DOCUMENT,
                )
        if content_type.startswith("audio/"):
            return cache_audio_from_bytes(payload, suffix), MessageType.AUDIO
        if content_type.startswith("video/"):
            return cache_video_from_bytes(payload, suffix), MessageType.VIDEO
        return cache_document_from_bytes(payload, safe_name), MessageType.DOCUMENT

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: str | None = None,
        metadata: Any = None,
    ) -> Any:
        return await self._send_parts(chat_id, content, reply_to, None)

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: str | None = None,
        reply_to: str | None = None,
        metadata: Any = None,
    ) -> Any:
        return await self._send_parts(chat_id, caption or "", reply_to, Path(image_url))

    async def send_document(
        self,
        chat_id: str,
        file_path: str,
        caption: str | None = None,
        file_name: str | None = None,
        reply_to: str | None = None,
        metadata: Any = None,
        **kwargs: Any,
    ) -> Any:
        return await self._send_parts(
            chat_id, caption or "", reply_to, Path(file_path), file_name
        )

    async def send_voice(
        self,
        chat_id: str,
        audio_path: str,
        caption: str | None = None,
        reply_to: str | None = None,
        metadata: Any = None,
        **kwargs: Any,
    ) -> Any:
        return await self._send_parts(
            chat_id, caption or "", reply_to, Path(audio_path)
        )

    async def get_chat_info(self, chat_id: str) -> dict[str, str]:
        """Return the address-based metadata required by Hermes adapters."""
        return {"name": chat_id, "type": "dm", "chat_id": chat_id}

    async def _send_parts(
        self,
        chat_id: str,
        content: str,
        reply_to: str | None,
        attachment: Path | None,
        file_name: str | None = None,
    ) -> Any:
        route = self._routes.get((chat_id.lower(), reply_to or ""))
        if _address(chat_id) != chat_id.lower() or route is None:
            return SendResult(
                success=False, error="explicit known recipient and reply route required"
            )
        try:
            message_id = await asyncio.to_thread(
                self._send_email, route, content, reply_to or "", attachment, file_name
            )
            self._routes[(route.chat_id, message_id)] = route
            self._router.record_outbound(route, message_id)
            return SendResult(success=True, message_id=message_id)
        except (OSError, smtplib.SMTPException, ValueError) as error:
            return SendResult(success=False, error=str(error))

    def _response_bodies(self, route: ThreadRoute, content: str) -> tuple[str, str]:
        """Render a response and add a quote only when its mode permits it."""
        context = self._router.context_for(route) or {}
        quote_source = context.get("quote_source", {})
        quote = str(quote_source.get("body", ""))
        include_quote = self._quote_mode == "always" or (
            self._quote_mode == "forwarded"
            and quote_source.get("is_forwarded") == "true"
        )
        html_body = render_markdown(content)
        if not include_quote or not quote:
            return content, html_body
        sender = str(quote_source.get("sender", route.chat_id))
        return quote_plain(content, quote, sender), quote_html(html_body, quote, sender)

    def _send_email(
        self,
        route: ThreadRoute,
        content: str,
        reply_to: str,
        attachment: Path | None,
        file_name: str | None,
    ) -> str:
        reply_ids = _message_ids(reply_to)
        if len(reply_ids) != 1:
            raise ValueError("reply_to must be one valid RFC Message-ID")
        context = self._router.context_for(route) or {}
        delivery = context.get("delivery_context", {})
        quote_source = context.get("quote_source", {})
        draft = context.get("draft_context", {})
        plain_body, html_body = self._response_bodies(route, content)

        subject = str(delivery.get("subject", "")).strip()
        fresh_draft = (
            draft.get("is_forwarded") == "true" and draft.get("draft_sent") == "false"
        )
        if fresh_draft:
            original_subject = str(draft.get("original_subject", "")).strip()
            subject = f"Draft: Re: {original_subject or 'Hermes Agent'}"
        elif not subject.lower().startswith("re:"):
            subject = f"Re: {subject}" if subject else "Re: Hermes Agent"
        recipient_name = str(delivery.get("display_name", ""))
        message = EmailMessage(policy=SMTP)
        message["From"] = Address(display_name="Hermes Agent", addr_spec=self._address)
        message["To"] = Address(display_name=recipient_name, addr_spec=route.chat_id)
        message["Subject"] = subject
        if not fresh_draft:
            message["In-Reply-To"] = reply_ids[0]
            references = _message_ids(str(quote_source.get("references", "")))
            message["References"] = " ".join(dict.fromkeys([*references, reply_ids[0]]))
        message["Date"] = formatdate(localtime=True)
        message_id = f"<hermes-{uuid.uuid4().hex}@{self._address.rsplit('@', 1)[-1]}>"
        message["Message-ID"] = message_id
        message.set_content(plain_body, charset="utf-8")
        message.add_alternative(html_body, subtype="html", charset="utf-8")
        if attachment is not None:
            data = attachment.read_bytes()
            content_type, _ = mimetypes.guess_type(file_name or attachment.name)
            maintype, subtype = (content_type or "application/octet-stream").split(
                "/", 1
            )
            message.make_mixed()
            message.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=file_name or attachment.name,
            )
        smtp = self._smtp()
        try:
            smtp.login(self._address, self._password)
            smtp.send_message(message)
        finally:
            smtp.quit()
        if fresh_draft:
            self._router.update_context(route, draft_context={"draft_sent": "true"})
        return message_id
