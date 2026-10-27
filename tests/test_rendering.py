"""Regression tests for safe outbound Markdown rendering."""

import html
from html.parser import HTMLParser

import pytest

from hermes_email_pp.rendering import render_markdown


@pytest.mark.parametrize("angle_brackets", [False, True])
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:18781/?token=TEST",
        "http://127.0.0.1:18781/?token=A%2BB%26C&document=review.pdf",
        "https://example.com/review?token=A%2BB%26C&document=review.pdf",
        "mailto:review@example.com?subject=Review&body=Please%20sign",
    ],
)
def test_markdown_links_preserve_destinations(url: str, angle_brackets: bool) -> None:
    destination = f"<{url}>" if angle_brackets else url

    rendered = render_markdown(f"[Review and sign document.pdf]({destination})")

    assert rendered == (
        f'<p><a href="{html.escape(url, quote=True)}">'
        "Review and sign document.pdf</a></p>"
    )

    destinations = []

    class LinkParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                destinations.append(dict(attrs).get("href"))

    LinkParser().feed(rendered)
    assert destinations == [url]


@pytest.mark.parametrize("angle_brackets", [False, True])
@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        "javascript&#58;alert(1)",
        "data:text/html,unsafe",
        "file:///workspace/report.pdf",
    ],
)
def test_markdown_links_block_unsafe_schemes(url: str, angle_brackets: bool) -> None:
    destination = f"<{url}>" if angle_brackets else url

    assert render_markdown(f"[unsafe]({destination})") == "<p><a>unsafe</a></p>"


@pytest.mark.parametrize(
    "raw_html",
    [
        "<script>alert(1)</script>",
        '<form action="https://evil.example"><input name="token"></form>',
        '<img src="https://evil.example" onerror="alert(1)">',
        '<a href="https://evil.example" onclick="alert(1)">link</a>',
        "<strong>raw formatting</strong>",
        '<div>\n<a href="https://evil.example">link</a>\n</div>',
        "<!-- untrusted comment -->",
    ],
)
def test_raw_html_remains_escaped(raw_html: str) -> None:
    assert render_markdown(raw_html) == f"<p>{html.escape(raw_html)}</p>"
    assert render_markdown(f"before {raw_html} after") == (
        f"<p>before {html.escape(raw_html)} after</p>"
    )


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            '`<script> & "value"`',
            "<p><code>&lt;script&gt; &amp; &quot;value&quot;</code></p>",
        ),
        (
            '```html\n<script> & "value"\n```',
            "<pre><code>&lt;script&gt; &amp; &quot;value&quot;\n</code></pre>",
        ),
    ],
)
def test_code_preserves_literal_html(body: str, expected: str) -> None:
    assert render_markdown(body) == expected
