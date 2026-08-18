"""Mocked transport tests for the Email++ adapter."""

from __future__ import annotations

import asyncio
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace

import pytest

from hermes_email_pp import adapter as adapter_module
from hermes_email_pp.adapter import (
    EmailPPAdapter,
    ThreadRoute,
    _address,
    _decode,
    _message_ids,
)
from hermes_email_pp.rendering import _SafeHTML


class Router:
    def __init__(self) -> None:
        self.outbound: list[tuple[ThreadRoute, str]] = []
        self.context: dict[str, dict[str, dict[str, str]]] = {}

    def resolve(self, sender: str, **kwargs: object) -> ThreadRoute:
        return ThreadRoute(sender, "email_pp:thread")

    def record_outbound(self, route: ThreadRoute, message_id: str) -> None:
        self.outbound.append((route, message_id))

    def update_context(self, route: ThreadRoute, **kwargs: object) -> None:
        context = self.context.setdefault(
            route.thread_id, {"delivery_context": {}, "quote_source": {}}
        )
        for name, values in kwargs.items():
            if values is not None:
                context[name].update(values)

    def context_for(self, route: ThreadRoute) -> dict[str, dict[str, str]] | None:
        return self.context.get(route.thread_id)


class IMAP:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.logged_out = False
        self.responses = {
            "ALL": ("OK", [b"1 2"]),
            "UNSEEN": ("OK", [b"3 4"]),
            "fetch": ("OK", [(None, b"From: person@example.com\n\nhello")]),
        }

    def login(self, *args: object) -> None:
        return None

    def select(self, mailbox: str) -> None:
        assert mailbox == "INBOX"

    def uid(self, command: str, *args: object):
        return self.responses[args[-1] if command == "search" else "fetch"]

    def logout(self) -> None:
        self.logged_out = True

    def shutdown(self) -> None:
        self.logged_out = True


class SMTP:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.started = False
        self.sent = None
        self.quit_called = False

    def starttls(self, **kwargs: object) -> None:
        self.started = True

    def login(self, *args: object) -> None:
        return None

    def send_message(self, message: object) -> None:
        self.sent = message

    def quit(self) -> None:
        self.quit_called = True


@pytest.fixture
def adapter(monkeypatch, tmp_path) -> EmailPPAdapter:
    monkeypatch.setattr(adapter_module, "EmailThreadRouter", Router)
    for name in (
        "EMAIL_PP_ADDRESS",
        "EMAIL_PP_PASSWORD",
        "EMAIL_PP_IMAP_HOST",
        "EMAIL_PP_SMTP_HOST",
        "EMAIL_PP_QUOTE_MODE",
    ):
        monkeypatch.delenv(name, raising=False)
    return EmailPPAdapter(
        SimpleNamespace(
            extra={
                "address": "agent@example.com",
                "password": "secret",
                "imap_host": "imap.example.com",
                "smtp_host": "smtp.example.com",
                "require_authenticated_sender": False,
            }
        )
    )


def test_header_helpers_are_safe() -> None:
    assert _address("Name <USER@example.com>") == "user@example.com"
    assert _address("not an address") == ""
    assert _decode("=?unknown?b?aGVsbG8=?=") == "hello"
    assert _message_ids("<one@example.com> <two@example.com>") == [
        "<one@example.com>",
        "<two@example.com>",
    ]
    assert _message_ids("<one@example.com>\nBcc: attacker@example.com") == []


def test_html_sanitizer_drops_unknown_tags_and_preserves_safe_entities() -> None:
    sanitizer = _SafeHTML()
    sanitizer.feed('<img src="https://evil.example"><br/>&#169;')

    assert "".join(sanitizer.parts) == "<br>&#169;"


def test_tls_baseline_fetch_and_reconnect(adapter, monkeypatch) -> None:
    instances: list[IMAP] = []

    def build_imap(*args: object, **kwargs: object) -> IMAP:
        instance = IMAP(*args, **kwargs)
        instances.append(instance)
        return instance

    monkeypatch.setattr(adapter_module.imaplib, "IMAP4_SSL", build_imap)
    adapter._baseline_mailbox(False)
    assert adapter._seen == {b"1", b"2"}
    assert instances[0].logged_out
    adapter._baseline_mailbox(True)
    assert adapter._seen == {b"1", b"2"}
    adapter._seen = {b"3"}
    assert adapter._fetch_unseen() == [b"From: person@example.com\n\nhello"]
    adapter._seen = {str(value).encode() for value in range(2001)}
    adapter._trim_seen()
    assert len(adapter._seen) == 1000
    no_messages = IMAP()
    no_messages.responses["UNSEEN"] = ("NO", [])
    monkeypatch.setattr(
        adapter_module.imaplib, "IMAP4_SSL", lambda *args, **kwargs: no_messages
    )
    assert adapter._fetch_unseen() == []
    no_messages.responses["UNSEEN"] = ("OK", [b"5"])
    no_messages.responses["fetch"] = ("NO", [])
    assert adapter._fetch_unseen() == []
    no_messages.responses["fetch"] = ("OK", [()])
    assert adapter._fetch_unseen() == []

    class BrokenIMAP:
        def logout(self) -> None:
            raise OSError("broken")

        def shutdown(self) -> None:
            raise OSError("also broken")

    adapter._close_imap(BrokenIMAP())


def test_smtp_tls_and_explicit_route_send(adapter, monkeypatch, tmp_path) -> None:
    smtp = SMTP()
    monkeypatch.setattr(adapter_module.smtplib, "SMTP", lambda *args, **kwargs: smtp)
    assert adapter._smtp() is smtp
    assert smtp.started
    secure = SMTP()
    adapter._smtp_port = 465
    monkeypatch.setattr(
        adapter_module.smtplib, "SMTP_SSL", lambda *args, **kwargs: secure
    )
    assert adapter._smtp() is secure

    route = ThreadRoute("person@example.com", "email_pp:thread")
    adapter._routes[(route.chat_id, "<inbound@example.com>")] = route
    attachment = tmp_path / "voice.ogg"
    attachment.write_bytes(b"audio")
    result = asyncio.run(
        adapter.send_voice(
            route.chat_id, str(attachment), reply_to="<inbound@example.com>"
        )
    )
    assert result.success
    assert adapter._router.outbound
    assert secure.sent["To"] == route.chat_id
    assert not asyncio.run(adapter.send("other@example.com", "no route")).success
    assert asyncio.run(
        adapter.send_image(
            route.chat_id, str(attachment), reply_to="<inbound@example.com>"
        )
    ).success
    assert asyncio.run(
        adapter.send_document(
            route.chat_id, str(attachment), reply_to="<inbound@example.com>"
        )
    ).success


def test_rich_mime_quotes_safe_html_and_encoded_headers(
    adapter, monkeypatch, tmp_path
) -> None:
    smtp = SMTP()
    monkeypatch.setattr(adapter, "_smtp", lambda: smtp)
    route = ThreadRoute("person@example.com", "email_pp:thread")
    adapter._router.update_context(
        route,
        delivery_context={
            "display_name": "Jos" + chr(0x00E9),
            "subject": "Weekly caf" + chr(0x00E9),
        },
        quote_source={
            "body": "<script>alert(1)</script>\n<img src=https://evil.example>",
            "sender": "person@example.com",
            "references": "<root@example.com> <inbound@example.com>",
            "is_forwarded": "false",
        },
    )
    content = """# Heading

**bold** and *emphasis* with [safe](https://example.com) and [bad](javascript:alert(1)).

- first
- second

Ordered:

1. one
2. two

| name | value |
| --- | --- |
| a | b |

`inline`

```python
print("code")
```

<form action="https://evil.example"><img src="https://evil.example"></form>"""
    adapter._send_email(route, content, "<inbound@example.com>", None, None)

    message = smtp.sent
    assert message.get_content_type() == "multipart/alternative"
    plain, rich = message.get_payload()
    plain_body = plain.get_payload(decode=True).decode()
    html_body = rich.get_payload(decode=True).decode()
    assert "> <script>alert(1)</script>" in plain_body
    for expected in ("<h1>", "<strong>", "<em>", "<ul>", "<ol>", "<table>", "<code>"):
        assert expected in html_body
    assert '<a href="https://example.com">safe</a>' in html_body
    assert "javascript:" not in html_body
    assert "<script" not in html_body
    assert "<form" not in html_body
    assert "<img" not in html_body
    assert message["In-Reply-To"] == "<inbound@example.com>"
    assert message["References"] == "<root@example.com> <inbound@example.com>"
    assert b"=?utf-8?" in message.as_bytes()

    attachment = tmp_path / "evidence.txt"
    attachment.write_bytes(b"evidence")
    adapter._send_email(route, "body", "<inbound@example.com>", attachment, None)

    message = smtp.sent
    assert message.get_content_type() == "multipart/mixed"
    body, attachment_part = message.get_payload()
    assert body.get_content_type() == "multipart/alternative"
    assert [part.get_content_type() for part in body.get_payload()] == [
        "text/plain",
        "text/html",
    ]
    assert attachment_part.get_content_disposition() == "attachment"


def test_quote_mode_defaults_validates_and_honors_forwarded_only(adapter) -> None:
    route = ThreadRoute("person@example.com", "email_pp:thread")
    adapter._router.update_context(
        route,
        quote_source={"body": "quoted", "sender": "person@example.com"},
    )
    assert adapter._quote_mode == "always"
    adapter._quote_mode = "never"
    assert "quoted" not in adapter._response_bodies(route, "body")[0]
    adapter._quote_mode = "forwarded"
    assert "quoted" not in adapter._response_bodies(route, "body")[0]
    adapter._router.update_context(route, quote_source={"is_forwarded": "true"})
    assert "quoted" in adapter._response_bodies(route, "body")[0]
    with pytest.raises(ValueError, match="reply_to"):
        adapter._send_email(route, "body", "not-a-message-id", None, None)
    with pytest.raises(ValueError, match="EMAIL_PP_QUOTE_MODE"):
        EmailPPAdapter(
            SimpleNamespace(
                extra={
                    "address": "agent@example.com",
                    "password": "secret",
                    "imap_host": "imap.example.com",
                    "smtp_host": "smtp.example.com",
                    "quote_mode": "sometimes",
                }
            )
        )


def test_authorization_mime_and_dispatch(adapter, monkeypatch) -> None:
    adapter._allowed = {"person@example.com"}
    message = EmailMessage()
    message["From"] = "person@example.com"
    message["Message-ID"] = "<inbound@example.com>"
    message.set_content("plain")
    message.add_alternative("<b>html</b>", subtype="html")
    message.add_attachment(b"image", maintype="image", subtype="png", filename="a.png")
    assert adapter._permitted("person@example.com", message)
    assert not adapter._permitted("noreply@example.com", message)
    assert not adapter._permitted("other@example.com", message)
    adapter._require_auth = True
    message["Authentication-Results"] = "mail.example; dmarc=pass"
    assert adapter._permitted("person@example.com", message)
    adapter._authserv_id = "expected.example"
    assert not adapter._permitted("person@example.com", message)
    adapter._authserv_id = ""
    adapter._require_auth = False
    text, urls, types, kind = adapter._content(message)
    assert text == "plain\n"
    assert types == ["image/png"]
    assert kind == adapter_module.MessageType.PHOTO
    assert Path(urls[0]).read_bytes() == b"image"

    handled: list[object] = []

    async def handle(event: object) -> None:
        handled.append(event)

    monkeypatch.setattr(adapter, "handle_message", handle)
    asyncio.run(adapter._dispatch(b"From: other@example.com\n\nignored"))
    assert not handled
    asyncio.run(adapter._dispatch(message.as_bytes()))
    assert handled[0].source.thread_id == "email_pp:thread"
    assert ("person@example.com", "<inbound@example.com>") in adapter._routes


def test_connect_disconnect_and_transport_failures(adapter, monkeypatch) -> None:
    calls: list[bool] = []

    def baseline(reconnect: bool) -> None:
        calls.append(reconnect)

    monkeypatch.setattr(adapter, "_baseline_mailbox", baseline)
    monkeypatch.setattr(adapter, "_probe_smtp", lambda: None)
    assert asyncio.run(adapter.connect(is_reconnect=True))
    assert calls == [True]
    asyncio.run(adapter.disconnect())
    adapter._address = ""
    assert not asyncio.run(adapter.connect())

    adapter._address = "agent@example.com"

    def unavailable(reconnect: bool) -> None:
        raise OSError("down")

    monkeypatch.setattr(adapter, "_baseline_mailbox", unavailable)
    assert not asyncio.run(adapter.connect())

    smtp = SMTP()
    monkeypatch.setattr(adapter, "_smtp", lambda: smtp)
    EmailPPAdapter._probe_smtp(adapter)
    assert smtp.quit_called
    route = ThreadRoute("person@example.com", "email_pp:thread")
    adapter._routes[(route.chat_id, "<inbound@example.com>")] = route

    def failed_send(*args: object) -> str:
        raise OSError("down")

    monkeypatch.setattr(adapter, "_send_email", failed_send)
    assert not asyncio.run(
        adapter.send(route.chat_id, "reply", "<inbound@example.com>")
    ).success
