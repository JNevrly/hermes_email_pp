"""Safe rich-text rendering for outbound Email++ messages."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import markdown  # type: ignore[import-untyped]

_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
_SAFE_LINK_SCHEMES = {"http", "https", "mailto"}
_LOCAL_MARKDOWN_LINK = r"\[([^\]]*)\]\(((?:~/|/|[A-Za-z]:[/\\])[^)\s]+)\)"
_MARKDOWN_IMAGE = r"!\[([^\]]*)\]\(([^)\s]+)\)"


def _email_markdown(body: str) -> str:
    """Keep image URLs and local-path references visible without fetching them."""

    def image_link(match: re.Match[str]) -> str:
        label, target = match.groups()
        return f"[{label or target}]({target})"

    def local_link(match: re.Match[str]) -> str:
        label, target = match.groups()
        return f"{label or target} (`{target}`)"

    body = re.sub(_MARKDOWN_IMAGE, image_link, body)
    return re.sub(_LOCAL_MARKDOWN_LINK, local_link, body)


class _SafeHTML(HTMLParser):
    """Retain renderer output only from a small, inert HTML allowlist."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in _ALLOWED_TAGS:
            return
        if tag == "a":
            href = next((value for name, value in attrs if name == "href"), None)
            if href and urlsplit(href).scheme.lower() in _SAFE_LINK_SCHEMES:
                self.parts.append(f'<a href="{html.escape(href, quote=True)}">')
                return
            self.parts.append("<a>")
            return
        self.parts.append(f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br" and tag in _ALLOWED_TAGS:
            self.parts.append("<br>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _ALLOWED_TAGS and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(html.escape(data))

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")


def render_markdown(body: str) -> str:
    """Convert Markdown to inert HTML without trusting model-provided HTML."""
    rendered = markdown.markdown(
        html.escape(_email_markdown(body)),
        extensions=["tables", "fenced_code"],
        output_format="html",
    )
    sanitizer = _SafeHTML()
    sanitizer.feed(rendered)
    sanitizer.close()
    return "".join(sanitizer.parts)


def quote_plain(body: str, quote: str, sender: str) -> str:
    """Append a conventional plain-text quote to an outbound response."""
    prefix = f"On {sender} wrote:\n" if sender else "Previous message:\n"
    quoted = "\n".join(f"> {line}" if line else ">" for line in quote.splitlines())
    return f"{body.rstrip()}\n\n{prefix}{quoted}\n"


def quote_html(body: str, quote: str, sender: str) -> str:
    """Append an escaped HTML quote without interpreting inbound content."""
    heading = f"On {html.escape(sender)} wrote:" if sender else "Previous message:"
    escaped_quote = html.escape(quote).replace("\n", "<br>\n")
    return f"{body}<hr><p>{heading}</p><blockquote>{escaped_quote}</blockquote>"
