"""Privacy-safe RFC email thread routing with profile-scoped persistence."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_MESSAGE_ID = r"<[^\s<>@]+@[^\s<>@]+>"
_MESSAGE_IDS = re.compile(rf"{_MESSAGE_ID}(?:\s+{_MESSAGE_ID})*")
_INDIVIDUAL_MESSAGE_ID = re.compile(_MESSAGE_ID)
_DEFAULT_RETENTION_DAYS = 90
DEFAULT_MAX_THREADS = 500


@dataclass(frozen=True)
class ThreadRoute:
    """The public routing values supplied to Hermes for one email message."""

    chat_id: str
    thread_id: str


def active_profile_home() -> Path:
    """Resolve Hermes' active profile directory without an eager dependency."""
    try:
        from hermes_constants import get_hermes_home  # type: ignore[import-not-found,import-untyped]  # noqa: I001
    except ImportError:
        return Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    return get_hermes_home()


def _message_ids(value: object) -> list[str] | None:
    """Parse a complete RFC Message-ID header, or reject it as malformed."""
    if value in (None, ""):
        return []
    if not isinstance(value, str):
        return None
    value = re.sub(r"\r?\n[ \t]+", " ", value)
    if "\r" in value or "\n" in value:
        return None
    value = value.strip()
    if not value or _MESSAGE_IDS.fullmatch(value) is None:
        return None
    return _INDIVIDUAL_MESSAGE_ID.findall(value)


class EmailThreadRouter:
    """Resolve and retain isolated email routes in the active Hermes profile."""

    def __init__(
        self,
        profile_home: Path | None = None,
        *,
        retention_days: int = _DEFAULT_RETENTION_DAYS,
        max_threads: int = DEFAULT_MAX_THREADS,
    ) -> None:
        self._path = (
            (profile_home or active_profile_home()) / "email_pp" / "threads.json"
        )
        self._retention_seconds = max(1, retention_days) * 24 * 60 * 60
        self._max_threads = max(1, max_threads)
        self._data = self._load()
        self._prune(time.time())

    def resolve(
        self,
        sender: str,
        *,
        message_id: object = None,
        references: object = None,
        in_reply_to: object = None,
    ) -> ThreadRoute:
        """Resolve a message route, refusing malformed headers to merge threads."""
        sender = sender.strip().lower()
        if not sender:
            raise ValueError("sender must be non-blank")

        message_ids = _message_ids(message_id)
        references_ids = _message_ids(references)
        reply_ids = _message_ids(in_reply_to)
        malformed = None in (message_ids, references_ids, reply_ids)
        aliases = self._data["aliases"]
        known = {
            aliases[key]["thread_id"]
            for identifier in (references_ids or []) + (reply_ids or [])
            if (key := self._alias_key(sender, identifier)) in aliases
        }

        if malformed or len(known) > 1:
            thread_id = self._isolated_thread_id()
        elif known:
            thread_id = known.pop()
        else:
            roots = references_ids or reply_ids or message_ids or []
            thread_id = (
                self._thread_id(sender, roots[0])
                if roots
                else self._isolated_thread_id()
            )

        now = time.time()
        thread = self._data["threads"].setdefault(
            thread_id,
            {
                "updated_at": now,
                "delivery_context": {"recipient": sender},
                "quote_source": {},
                "draft_context": {},
            },
        )
        thread["updated_at"] = now
        if message_ids:
            aliases[self._alias_key(sender, message_ids[0])] = {
                "thread_id": thread_id,
                "updated_at": now,
            }
        self._prune(now)
        self._save()
        return ThreadRoute(chat_id=sender, thread_id=thread_id)

    def record_outbound(self, route: ThreadRoute, message_id: object) -> None:
        """Associate a generated Message-ID with its existing thread."""
        message_ids = _message_ids(message_id)
        if message_ids is None or len(message_ids) != 1:
            raise ValueError("message_id must be a valid RFC Message-ID")
        thread = self._data["threads"].get(route.thread_id)
        if (
            thread is None
            or thread["delivery_context"].get("recipient") != route.chat_id
        ):
            raise ValueError("route is not known for this recipient")
        now = time.time()
        thread["updated_at"] = now
        self._data["aliases"][self._alias_key(route.chat_id, message_ids[0])] = {
            "thread_id": route.thread_id,
            "updated_at": now,
        }
        self._prune(now)
        self._save()

    def update_context(
        self,
        route: ThreadRoute,
        *,
        delivery_context: Mapping[str, str] | None = None,
        quote_source: Mapping[str, str] | None = None,
        draft_context: Mapping[str, str] | None = None,
    ) -> None:
        """Persist bounded, JSON-safe delivery, quote, and draft details."""
        thread = self._data["threads"].get(route.thread_id)
        if (
            thread is None
            or thread["delivery_context"].get("recipient") != route.chat_id
        ):
            raise ValueError("route is not known for this recipient")
        for name, values in (
            ("delivery_context", delivery_context),
            ("quote_source", quote_source),
            ("draft_context", draft_context),
        ):
            if values is not None:
                thread[name].update(
                    {str(key): str(value) for key, value in values.items()}
                )
        thread["updated_at"] = time.time()
        self._prune(thread["updated_at"])
        self._save()

    def context_for(self, route: ThreadRoute) -> dict[str, dict[str, str]] | None:
        """Return a copy of context only when it belongs to the recipient."""
        thread = self._data["threads"].get(route.thread_id)
        if (
            thread is None
            or thread["delivery_context"].get("recipient") != route.chat_id
        ):
            return None
        return {
            name: dict(thread[name])
            for name in ("delivery_context", "quote_source", "draft_context")
        }

    def _alias_key(self, sender: str, message_id: str) -> str:
        return hashlib.sha256(f"{sender}\0{message_id}".encode()).hexdigest()

    def _thread_id(self, sender: str, root: str) -> str:
        digest = hmac.new(
            self._data["secret"].encode(), f"{sender}\0{root}".encode(), hashlib.sha256
        ).hexdigest()
        return f"email_pp:{digest[:32]}"

    def _isolated_thread_id(self) -> str:
        return f"email_pp:{secrets.token_hex(16)}"

    def _load(self) -> dict[str, Any]:
        try:
            with self._path.open(encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, json.JSONDecodeError):
            loaded = {}
        if not isinstance(loaded, dict):
            loaded = {}
        secret = loaded.get("secret")
        threads = loaded.get("threads")
        aliases = loaded.get("aliases")
        return {
            "secret": (
                secret if isinstance(secret, str) and secret else secrets.token_hex(32)
            ),
            "threads": threads if isinstance(threads, dict) else {},
            "aliases": aliases if isinstance(aliases, dict) else {},
        }

    def _prune(self, now: float) -> None:
        threads = self._data["threads"]
        cutoff = now - self._retention_seconds
        valid = {
            thread_id
            for thread_id, thread in threads.items()
            if isinstance(thread, dict) and thread.get("updated_at", 0) >= cutoff
        }
        if len(valid) > self._max_threads:
            valid = set(
                sorted(valid, key=lambda thread_id: threads[thread_id]["updated_at"])[
                    -self._max_threads :
                ]
            )
        self._data["threads"] = {
            thread_id: thread
            for thread_id, thread in threads.items()
            if thread_id in valid
        }
        self._data["aliases"] = {
            key: alias
            for key, alias in self._data["aliases"].items()
            if isinstance(alias, dict) and alias.get("thread_id") in valid
        }

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self._path.parent, 0o700)
        descriptor, temporary = tempfile.mkstemp(
            dir=self._path.parent, prefix=".threads-", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                os.fchmod(handle.fileno(), 0o600)
                json.dump(self._data, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._path)
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise
