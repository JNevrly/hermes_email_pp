"""Tests for the Email++ plugin registration contract."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from types import ModuleType, SimpleNamespace

from hermes_email_pp.config import REQUIRED_ENV, environment_enablement, is_configured
from hermes_email_pp.plugin import check_requirements, create_adapter, register


class RecordingContext:
    """Minimal Hermes plugin context used to inspect registration arguments."""

    def register_platform(self, **kwargs: object) -> None:
        self.registration = kwargs


def test_project_declares_email_pp_entry_point() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text())

    assert project["project"]["entry-points"]["hermes_agent.plugins"] == {
        "email-pp": "hermes_email_pp.plugin:register"
    }
    assert project["project"]["requires-python"] == ">=3.11,<3.14"
    assert project["project"]["dependencies"] == [
        "hermes-agent @ "
        "git+https://github.com/NousResearch/hermes-agent.git@"
        "e02d1e41fc6104187e20af9eac8b2820566e3508"
    ]


def test_registers_email_pp_with_isolated_access_control() -> None:
    context = RecordingContext()

    register(context)

    assert context.registration["name"] == "email_pp"
    assert context.registration["required_env"] == list(REQUIRED_ENV)
    assert context.registration["allowed_users_env"] == "EMAIL_PP_ALLOWED_USERS"
    assert context.registration["allow_all_env"] == "EMAIL_PP_ALLOW_ALL_USERS"


def test_configuration_never_reads_builtin_email_settings(monkeypatch) -> None:
    monkeypatch.setenv("EMAIL_ADDRESS", "built-in@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "built-in-secret")
    monkeypatch.setenv("EMAIL_IMAP_HOST", "imap.example.com")
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.example.com")

    assert check_requirements()
    assert not is_configured(SimpleNamespace(extra={}))
    assert environment_enablement() is None


def test_configuration_accepts_email_pp_environment(monkeypatch) -> None:
    for name, value in zip(
        REQUIRED_ENV,
        ("agent@example.com", "secret", "imap.example.com", "smtp.example.com"),
        strict=True,
    ):
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("EMAIL_PP_IMAP_PORT", "993")

    assert is_configured(SimpleNamespace(extra={}))
    assert environment_enablement() == {
        "address": "agent@example.com",
        "password": "secret",
        "imap_host": "imap.example.com",
        "smtp_host": "smtp.example.com",
        "imap_port": "993",
    }


def test_configuration_accepts_platform_extra_without_environment() -> None:
    config = SimpleNamespace(
        extra={
            "address": "agent@example.com",
            "password": "secret",
            "imap_host": "imap.example.com",
            "smtp_host": "smtp.example.com",
        }
    )

    assert is_configured(config, environ={})


def test_configuration_rejects_non_mapping_platform_extra() -> None:
    assert not is_configured(SimpleNamespace(extra=[]), environ={})


def test_adapter_factory_defers_transport_import(monkeypatch) -> None:
    config = SimpleNamespace()
    adapter_module = ModuleType("hermes_email_pp.adapter")

    class FakeAdapter:
        def __init__(self, received_config: object) -> None:
            self.config = received_config

    adapter_module.EmailPPAdapter = FakeAdapter
    monkeypatch.setitem(sys.modules, "hermes_email_pp.adapter", adapter_module)

    assert create_adapter(config).config is config
