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
)

# Plain dictionaries keep this metadata importable on Hermes 0.20.5, which
# predates the richer PlatformField registration contract.
CHANNEL_FIELDS = (
    {
        "key": "EMAIL_PP_ADDRESS",
        "label": "Email address",
        "description": "Mailbox address and SMTP envelope identity.",
        "required": True,
    },
    {
        "key": "EMAIL_PP_PASSWORD",
        "label": "Email password",
        "description": "Mailbox password or provider-issued app password.",
        "password": True,
        "input_type": "password",
        "required": True,
    },
    {
        "key": "EMAIL_PP_IMAP_HOST",
        "label": "IMAP host",
        "description": "IMAP server hostname, for example imap.example.com.",
        "required": True,
    },
    {
        "key": "EMAIL_PP_SMTP_HOST",
        "label": "SMTP host",
        "description": "SMTP server hostname, for example smtp.example.com.",
        "required": True,
    },
    {
        "key": "EMAIL_PP_IMAP_PORT",
        "label": "IMAP port",
        "description": "IMAP-over-TLS port.",
        "input_type": "number",
        "default": 993,
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_SMTP_PORT",
        "label": "SMTP port",
        "description": "SMTP STARTTLS port; use 465 for implicit TLS.",
        "input_type": "number",
        "default": 587,
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_POLL_INTERVAL",
        "label": "Poll interval (seconds)",
        "description": (
            "Inbox polling interval. Values below one second become one second."
        ),
        "input_type": "number",
        "default": 15,
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_MAILBOX",
        "label": "Mailbox",
        "description": "Mailbox selected for polling.",
        "default": "INBOX",
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_ALLOWED_USERS",
        "label": "Allowed sender addresses",
        "description": (
            "Comma-separated sender-address allowlist. Required unless allow all "
            "users is enabled."
        ),
    },
    {
        "key": "EMAIL_PP_ALLOW_ALL_USERS",
        "label": "Allow all users",
        "description": "Accept every non-automated sender.",
        "input_type": "boolean",
        "default": False,
        "advanced": True,
        "warning": (
            "This bypasses the allowlist and sender-authentication checks. Do not "
            "enable it for an Internet-facing mailbox."
        ),
    },
    {
        "key": "EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER",
        "label": "Require authenticated sender",
        "description": "Require a passing DMARC result for allowlisted senders.",
        "input_type": "boolean",
        "default": True,
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_AUTHSERV_ID",
        "label": "Authentication service ID",
        "description": (
            "Optional service identifier that must prefix the trusted "
            "Authentication-Results header."
        ),
        "advanced": True,
    },
    {
        "key": "EMAIL_PP_QUOTE_MODE",
        "label": "Quote mode",
        "description": "Controls when the source email is visibly quoted in a reply.",
        "input_type": "select",
        "default": "always",
        "options": ("always", "forwarded", "never"),
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


def is_configured(config: Any, environ: Mapping[str, str] | None = None) -> bool:
    """Return whether isolated environment or platform config supplies all secrets."""
    extra = getattr(config, "extra", {})
    if not isinstance(extra, Mapping):
        return False
    settings = environment_settings(environ)
    return all(
        settings.get(name) or str(extra.get(_CONFIG_KEYS[name], "")).strip()
        for name in REQUIRED_ENV
    )


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
