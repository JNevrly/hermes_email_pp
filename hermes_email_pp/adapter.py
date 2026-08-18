"""Secure IMAP/SMTP transport for the Email++ Hermes platform."""

from __future__ import annotations

import asyncio
import email
import imaplib
import mimetypes
import re
import smtplib
import ssl
import uuid
from email.header import decode_header
from email.headerregistry import Address
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formatdate, parseaddr
from pathlib import Path
from typing import Any

from hermes_email_pp.config import environment_settings
from hermes_email_pp.rendering import quote_html, quote_plain, render_markdown
from hermes_email_pp.threading import EmailThreadRouter, ThreadRoute

try:
    from gateway.config import Platform  # type: ignore[import-not-found]
    from gateway.platforms.base import (  # type: ignore[import-not-found]  # pragma: no cover
        BasePlatformAdapter,
        MessageEvent,
        MessageType,
        SendResult,
    )
except ImportError:  # pragma: no cover - supports isolated package tests

    class BasePlatformAdapter:  # type: ignore[no-redef]
        def __init__(self, config: Any, platform: Any) -> None:
            self.config = config
            self.platform = platform
            self._running = False

        def build_source(self, **kwargs: Any) -> Any:
            return type("Source", (), kwargs)()

        async def handle_message(self, event: Any) -> None:
            return None

    class MessageType:  # type: ignore[no-redef]
        TEXT = "text"
        PHOTO = "photo"
        DOCUMENT = "document"

    class MessageEvent:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            self.__dict__.update(kwargs)

    class SendResult:  # type: ignore[no-redef]
        def __init__(self, success: bool, **kwargs: Any) -> None:
            self.success = success
            self.__dict__.update(kwargs)

    Platform = type("Platform", (), {"EMAIL_PP": "email_pp"})


_AUTOMATED = ("noreply", "no-reply", "mailer-daemon", "postmaster", "bounce")
_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MESSAGE_ID = re.compile(r"<[^\s<>@]+@[^\s<>@]+>")
_MESSAGE_IDS = re.compile(r"<[^\s<>@]+@[^\s<>@]+>(?:\s+<[^\s<>@]+@[^\s<>@]+>)*")


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

    _seen_by_address: dict[str, set[bytes]] = {}

    def __init__(self, config: Any) -> None:
        super().__init__(config, getattr(Platform, "EMAIL_PP", "email_pp"))
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
        self._allowed = {
            value.strip().lower()
            for value in settings.get("EMAIL_PP_ALLOWED_USERS", "").split(",")
            if _address(value)
        }
        self._allow_all = settings.get("EMAIL_PP_ALLOW_ALL_USERS", "").lower() in {
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
        self._seen: set[bytes] = set()
        self._poll_task: asyncio.Task[None] | None = None
        self._routes: dict[tuple[str, str], ThreadRoute] = {}
        self._router = EmailThreadRouter()

    @staticmethod
    def _setting(settings: dict[str, str], extra: Any, env: str, key: str) -> str:
        return str(settings.get(env) or extra.get(key, "")).strip()

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
            return False
        try:
            await asyncio.to_thread(self._baseline_mailbox, is_reconnect)
            await asyncio.to_thread(self._probe_smtp)
        except (OSError, imaplib.IMAP4.error, smtplib.SMTPException):
            return False
        self._running = True
        self._poll_task = asyncio.create_task(self._poll_loop())
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

    def _baseline_mailbox(self, is_reconnect: bool) -> None:
        imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, timeout=30)
        try:
            imap.login(self._address, self._password)
            imap.select(self._mailbox)
            if is_reconnect and self._address in self._seen_by_address:
                self._seen = set(self._seen_by_address[self._address])
                return
            status, data = imap.uid("search", "", "ALL")
            self._seen = set(data[0].split()) if status == "OK" and data else set()
            self._trim_seen()
        finally:
            self._close_imap(imap)
        self._seen_by_address[self._address] = set(self._seen)

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
                for raw in await asyncio.to_thread(self._fetch_unseen):
                    try:
                        await self._dispatch(raw)
                    except Exception:
                        continue
            except asyncio.CancelledError:
                raise
            except Exception:
                pass
            await asyncio.sleep(max(1, self._poll_interval))

    def _fetch_unseen(self) -> list[bytes]:
        imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, timeout=30)
        messages: list[bytes] = []
        try:
            imap.login(self._address, self._password)
            imap.select(self._mailbox)
            status, data = imap.uid("search", "", "UNSEEN")
            if status != "OK" or not data:
                return messages
            for uid in data[0].split():
                if uid in self._seen:
                    continue
                status, data = imap.uid("fetch", uid, "(RFC822)")
                if status != "OK" or not data:
                    continue
                try:
                    raw = data[0][1]
                except (IndexError, TypeError):
                    continue
                if isinstance(raw, bytes):
                    self._seen.add(uid)
                    messages.append(raw)
            self._trim_seen()
            return messages
        finally:
            self._close_imap(imap)
            self._seen_by_address[self._address] = set(self._seen)

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
        message_ids = _message_ids(message_id)
        references = _message_ids(message.get("References", ""))
        if message_ids:
            references.append(message_ids[0])
        self._router.update_context(
            route,
            delivery_context={
                "display_name": _display_name(message.get("From", sender)),
                "subject": _decode(message.get("Subject", "")),
            },
            quote_source={
                "body": text[:100_000],
                "sender": sender,
                "references": " ".join(dict.fromkeys(references)),
                "is_forwarded": "false",
            },
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
                text=text or "(empty email)",
                message_type=message_type,
                source=source,
                message_id=message_id or None,
                reply_to_message_id=message.get("In-Reply-To") or None,
                media_urls=urls,
                media_types=types,
            )
        )

    def _permitted(self, sender: str, message: Any) -> bool:
        if (
            not sender
            or sender == self._address.lower()
            or any(x in sender for x in _AUTOMATED)
        ):
            return False
        if not self._allow_all and sender not in self._allowed:
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
                suffix = Path(part.get_filename() or "attachment").suffix or ".bin"
                path = Path("/tmp") / f"email-pp-{uuid.uuid4().hex}{suffix}"
                path.write_bytes(payload)
                urls.append(str(path))
                types.append(content_type)
                message_type = (
                    MessageType.PHOTO
                    if content_type in _IMAGE_TYPES
                    else MessageType.DOCUMENT
                )
        return text or html, urls, types, message_type

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
        plain_body, html_body = self._response_bodies(route, content)

        subject = str(delivery.get("subject", "")).strip()
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}" if subject else "Re: Hermes Agent"
        recipient_name = str(delivery.get("display_name", ""))
        message = EmailMessage(policy=SMTP)
        message["From"] = Address(display_name="Hermes Agent", addr_spec=self._address)
        message["To"] = Address(display_name=recipient_name, addr_spec=route.chat_id)
        message["Subject"] = subject
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
        return message_id
