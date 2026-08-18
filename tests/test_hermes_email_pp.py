"""Tests for the Email++ plugin registration contract."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from hermes_email_pp import threading as email_threading
from hermes_email_pp.config import REQUIRED_ENV, environment_enablement, is_configured
from hermes_email_pp.plugin import check_requirements, create_adapter, register
from hermes_email_pp.threading import EmailThreadRouter, ThreadRoute


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


def test_unrelated_messages_from_one_sender_get_isolated_threads(tmp_path) -> None:
    router = EmailThreadRouter(tmp_path)

    first = router.resolve("person@example.com", message_id="<first@example.com>")
    second = router.resolve("person@example.com", message_id="<second@example.com>")

    assert first.chat_id == second.chat_id == "person@example.com"
    assert first.thread_id != second.thread_id
    assert "example.com" not in first.thread_id
    assert "first" not in first.thread_id


def test_references_and_generated_aliases_continue_a_thread_after_restart(
    tmp_path,
) -> None:
    first = EmailThreadRouter(tmp_path).resolve(
        "person@example.com", message_id="<root@example.com>"
    )
    router = EmailThreadRouter(tmp_path)
    router.record_outbound(first, "<hermes-1@agent.example>")
    router.update_context(
        first,
        quote_source={"message_id": "<root@example.com>"},
        draft_context={"subject": "Draft"},
    )

    restarted = EmailThreadRouter(tmp_path)
    via_references = restarted.resolve(
        "person@example.com",
        message_id="<reply@example.com>",
        references="<root@example.com> <hermes-1@agent.example>",
    )
    via_generated_alias = restarted.resolve(
        "person@example.com",
        message_id="<reply-two@example.com>",
        in_reply_to="<hermes-1@agent.example>",
    )

    assert via_references.thread_id == first.thread_id == via_generated_alias.thread_id
    assert restarted.context_for(first) == {
        "delivery_context": {"recipient": "person@example.com"},
        "quote_source": {"message_id": "<root@example.com>"},
        "draft_context": {"subject": "Draft"},
    }
    assert (tmp_path / "email_pp" / "threads.json").stat().st_mode & 0o777 == 0o600
    assert (tmp_path / "email_pp").stat().st_mode & 0o777 == 0o700


def test_sender_scope_and_malformed_headers_cannot_merge_threads(tmp_path) -> None:
    router = EmailThreadRouter(tmp_path)
    first = router.resolve("first@example.com", message_id="<root@example.com>")
    other_sender = router.resolve(
        "second@example.com",
        message_id="<reply@example.com>",
        references="<root@example.com>",
    )
    malformed = router.resolve(
        "first@example.com",
        message_id="<reply@example.com>",
        references="not-a-message-id",
        in_reply_to="<root@example.com>",
    )

    assert other_sender.thread_id != first.thread_id
    assert malformed.thread_id != first.thread_id
    assert (
        router.context_for(ThreadRoute("second@example.com", first.thread_id)) is None
    )


def test_context_and_outbound_alias_reject_unknown_or_cross_recipient_routes(
    tmp_path,
) -> None:
    router = EmailThreadRouter(tmp_path, max_threads=1)
    route = router.resolve("person@example.com", message_id="<root@example.com>")
    other = ThreadRoute("other@example.com", route.thread_id)

    with pytest.raises(ValueError, match="valid RFC"):
        router.record_outbound(route, "not-an-id")
    with pytest.raises(ValueError, match="not known"):
        router.record_outbound(other, "<hermes@agent.example>")
    with pytest.raises(ValueError, match="not known"):
        router.update_context(
            other, delivery_context={"recipient": "other@example.com"}
        )

    router.resolve("person@example.com", message_id="<second@example.com>")

    assert router.context_for(route) is None


def test_threading_header_validation_and_profile_home_resolution(
    monkeypatch, tmp_path
) -> None:
    assert email_threading._message_ids(1) is None
    assert email_threading._message_ids("<one@example.com>\n<two@example.com>") is None
    assert email_threading._message_ids("<one@example.com> <two@example.com>") == [
        "<one@example.com>",
        "<two@example.com>",
    ]
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.delitem(sys.modules, "hermes_constants", raising=False)

    assert email_threading.active_profile_home() == tmp_path
    hermes_constants = ModuleType("hermes_constants")
    hermes_constants.get_hermes_home = lambda: tmp_path / "active"
    monkeypatch.setitem(sys.modules, "hermes_constants", hermes_constants)

    assert email_threading.active_profile_home() == tmp_path / "active"


def test_threading_rejects_blank_sender_and_discards_invalid_persisted_data(
    tmp_path,
) -> None:
    state_path = tmp_path / "email_pp" / "threads.json"
    state_path.parent.mkdir()
    state_path.write_text("[]")
    router = EmailThreadRouter(tmp_path)

    with pytest.raises(ValueError, match="non-blank"):
        router.resolve(" ")

    route = router.resolve("person@example.com")

    assert route.thread_id.startswith("email_pp:")
    assert router.context_for(route) == {
        "delivery_context": {"recipient": "person@example.com"},
        "quote_source": {},
        "draft_context": {},
    }


def test_conflicting_known_aliases_fail_toward_isolation_and_retention_is_bounded(
    tmp_path,
) -> None:
    router = EmailThreadRouter(tmp_path, retention_days=1, max_threads=3)
    first = router.resolve("person@example.com", message_id="<first@example.com>")
    second = router.resolve("person@example.com", message_id="<second@example.com>")

    conflicting = router.resolve(
        "person@example.com",
        message_id="<conflict@example.com>",
        references="<first@example.com> <second@example.com>",
    )
    router._max_threads = 1
    router._data["threads"][conflicting.thread_id]["updated_at"] = 0
    router._prune(2 * 24 * 60 * 60)

    assert conflicting.thread_id not in router._data["threads"]
    assert first.thread_id != second.thread_id != conflicting.thread_id


def test_failed_state_write_removes_its_temporary_file(tmp_path, monkeypatch) -> None:
    router = EmailThreadRouter(tmp_path)

    def fail_replace(*args) -> None:
        raise OSError("disk failure")

    monkeypatch.setattr(email_threading.os, "replace", fail_replace)
    monkeypatch.setattr(email_threading.os, "unlink", fail_replace)

    with pytest.raises(OSError, match="disk failure"):
        router.resolve("person@example.com", message_id="<root@example.com>")
