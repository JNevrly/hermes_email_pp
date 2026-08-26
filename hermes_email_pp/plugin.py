"""Hermes entry point for the Email++ platform."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .config import CHANNEL_FIELDS, REQUIRED_ENV, environment_enablement, is_configured


def check_requirements() -> bool:
    """Email++ uses only Python's standard-library IMAP and SMTP clients."""
    return True


def create_adapter(config: Any) -> Any:
    """Load the transport only when the gateway creates the Email++ adapter."""
    adapter_module = import_module(".adapter", package=__package__)
    return adapter_module.EmailPPAdapter(config)


def register(ctx: Any) -> None:
    """Register Email++ without touching Hermes' built-in email platform."""
    registration: dict[str, Any] = {
        "name": "email_pp",
        "label": "Email++",
        "adapter_factory": create_adapter,
        "check_fn": check_requirements,
        "validate_config": is_configured,
        "is_connected": is_configured,
        "required_env": list(REQUIRED_ENV),
        "env_enablement_fn": environment_enablement,
        "allowed_users_env": "EMAIL_PP_ALLOWED_USERS",
        "allow_all_env": "EMAIL_PP_ALLOW_ALL_USERS",
        "emoji": "email",
        "platform_hint": (
            "You are responding by email. Keep replies clear and professional."
        ),
    }
    try:
        PlatformField = import_module("gateway.platform_registry").PlatformField
    except (AttributeError, ImportError):
        # Hermes 0.20.5 has no rich descriptor API. Its required_env card is
        # still sufficient to configure the credentials needed for Email++.
        pass
    else:
        registration["fields"] = [PlatformField(**field) for field in CHANNEL_FIELDS]
    ctx.register_platform(**registration)
