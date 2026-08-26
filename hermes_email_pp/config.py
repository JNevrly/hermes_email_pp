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
