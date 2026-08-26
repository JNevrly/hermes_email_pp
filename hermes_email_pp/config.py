"""Configuration shared by the Email++ platform registration and adapter."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

REQUIRED_ENV = (
    "EMAIL_PP_ADDRESS",
    "EMAIL_PP_PASSWORD",
    "EMAIL_PP_IMAP_HOST",
    "EMAIL_PP_SMTP_HOST",
)

OPTIONAL_ENV = (
    "EMAIL_PP_IMAP_PORT",
    "EMAIL_PP_SMTP_PORT",
    "EMAIL_PP_POLL_INTERVAL",
    "EMAIL_PP_MAILBOX",
    "EMAIL_PP_ALLOWED_USERS",
    "EMAIL_PP_ALLOW_ALL_USERS",
    "EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER",
    "EMAIL_PP_AUTHSERV_ID",
    "EMAIL_PP_QUOTE_MODE",
    "EMAIL_PP_PROCESS_HISTORY_WINDOW",
)

# Vanilla Hermes suppresses *_ALLOW_ALL_USERS optional fields from setup cards.
# Keep this visible in Channels by requiring the explicit secure value "false".
CHANNEL_REQUIRED_ENV = (*REQUIRED_ENV, "EMAIL_PP_ALLOW_ALL_USERS")

# Metadata consumed by vanilla Hermes' OPTIONAL_ENV_VARS registry. The stock
# Channels card renders each entry as a text or password input.
CHANNEL_ENV = (
    {
        "name": "EMAIL_PP_ADDRESS",
        "prompt": "Email address",
        "description": "Mailbox address and SMTP envelope identity.",
    },
    {
        "name": "EMAIL_PP_PASSWORD",
        "prompt": "Email password",
        "description": "Mailbox password or provider-issued app password.",
        "password": True,
    },
    {
        "name": "EMAIL_PP_IMAP_HOST",
        "prompt": "IMAP host",
        "description": "IMAP server hostname, for example imap.example.com.",
    },
    {
        "name": "EMAIL_PP_SMTP_HOST",
        "prompt": "SMTP host",
        "description": "SMTP server hostname, for example smtp.example.com.",
    },
    {
        "name": "EMAIL_PP_IMAP_PORT",
        "prompt": "IMAP port",
        "description": "IMAP-over-TLS port. Default: 993.",
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_SMTP_PORT",
        "prompt": "SMTP port",
        "description": "SMTP STARTTLS port; use 465 for implicit TLS. Default: 587.",
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_POLL_INTERVAL",
        "prompt": "Poll interval (seconds)",
        "description": (
            "Inbox polling interval. Values below one second become one second. "
            "Default: 15."
        ),
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_MAILBOX",
        "prompt": "Mailbox",
        "description": "Mailbox selected for polling. Default: INBOX.",
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_ALLOWED_USERS",
        "prompt": "Allowed sender addresses",
        "description": (
            "Comma-separated sender-address allowlist. Required unless allow all "
            "users is enabled."
        ),
    },
    {
        "name": "EMAIL_PP_ALLOW_ALL_USERS",
        "prompt": "Allow all users",
        "advanced": True,
        "description": (
            "Enter true to accept every non-automated sender. Default: false. "
            "WARNING: this bypasses the allowlist and sender-authentication "
            "checks; do not enable it for an Internet-facing mailbox."
        ),
    },
    {
        "name": "EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER",
        "prompt": "Require authenticated sender",
        "description": (
            "Enter true to require a passing DMARC result for allowlisted senders. "
            "Default: true."
        ),
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_AUTHSERV_ID",
        "prompt": "Authentication service ID",
        "description": (
            "Optional service identifier that must prefix the trusted "
            "Authentication-Results header."
        ),
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_QUOTE_MODE",
        "prompt": "Quote mode",
        "description": (
            "Controls when the source email is visibly quoted. Enter always, "
            "forwarded, or never. Default: always."
        ),
        "advanced": True,
    },
    {
        "name": "EMAIL_PP_PROCESS_HISTORY_WINDOW",
        "prompt": "Process unread history window (seconds)",
        "description": (
            "Process unread email already in the mailbox at startup. Enter 0 to "
            "skip it, -1 to process all of it, or a positive number of seconds "
            "to process only recent email. Default: 0."
        ),
        "advanced": True,
    },
)

_CONFIG_KEYS = {
    "EMAIL_PP_ADDRESS": "address",
    "EMAIL_PP_PASSWORD": "password",
    "EMAIL_PP_IMAP_HOST": "imap_host",
    "EMAIL_PP_SMTP_HOST": "smtp_host",
    "EMAIL_PP_IMAP_PORT": "imap_port",
    "EMAIL_PP_SMTP_PORT": "smtp_port",
    "EMAIL_PP_POLL_INTERVAL": "poll_interval",
    "EMAIL_PP_MAILBOX": "mailbox",
    "EMAIL_PP_ALLOWED_USERS": "allowed_users",
    "EMAIL_PP_ALLOW_ALL_USERS": "allow_all_users",
    "EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER": "require_authenticated_sender",
    "EMAIL_PP_AUTHSERV_ID": "authserv_id",
    "EMAIL_PP_QUOTE_MODE": "quote_mode",
    "EMAIL_PP_PROCESS_HISTORY_WINDOW": "process_history_window",
}


def _secret(name: str) -> str:
    """Read a profile-scoped value, preserving the default-profile fallback."""
    try:
        from agent.secret_scope import (  # type: ignore[import-not-found]
            UnscopedSecretError,
            get_secret,
        )
    except ImportError:
        return os.environ.get(name, "")
    try:
        return get_secret(name, "") or ""
    except UnscopedSecretError:
        return os.environ.get(name, "")


def environment_settings(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return non-blank Email++ settings without consulting built-in email vars."""
    values = environ
    return {
        key: value.strip()
        for key in (*REQUIRED_ENV, *OPTIONAL_ENV)
        if (
            value := (values.get(key, "") if values is not None else _secret(key))
        ).strip()
    }


def process_history_window(value: object) -> int:
    """Validate the optional unread cold-start recovery window."""
    raw = str(value).strip()
    if not raw:
        return 0
    try:
        window = int(raw)
    except ValueError as error:
        raise ValueError(
            "EMAIL_PP_PROCESS_HISTORY_WINDOW must be an integer greater than "
            "or equal to -1"
        ) from error
    if window < -1:
        raise ValueError(
            "EMAIL_PP_PROCESS_HISTORY_WINDOW must be an integer greater than "
            "or equal to -1"
        )
    return window


def is_configured(config: Any, environ: Mapping[str, str] | None = None) -> bool:
    """Return whether isolated environment or platform config supplies all secrets."""
    extra = getattr(config, "extra", {})
    if not isinstance(extra, Mapping):
        return False
    settings = environment_settings(environ)
    configured = all(
        settings.get(name) or str(extra.get(_CONFIG_KEYS[name], "")).strip()
        for name in REQUIRED_ENV
    )
    if not configured:
        return False
    process_history_window(
        settings.get(
            "EMAIL_PP_PROCESS_HISTORY_WINDOW",
            extra.get("process_history_window", ""),
        )
    )
    return True


def environment_enablement() -> dict[str, str] | None:
    """Seed platform extras only when all required Email++ variables are set."""
    settings = environment_settings()
    if not all(settings.get(name) for name in REQUIRED_ENV):
        return None
    return {
        _CONFIG_KEYS[name]: value
        for name, value in settings.items()
        if name in _CONFIG_KEYS
    }
