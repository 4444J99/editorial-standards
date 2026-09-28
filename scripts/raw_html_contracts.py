"""Retain real anchor destinations without promoting raw HTML to Markdown."""

from html import escape
from html.parser import HTMLParser


class _RawAnchorParser(HTMLParser):
    """Extract first-href anchors outside comments and raw-text elements."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.destinations = []
        self.raw_text_tag = None

    def handle_starttag(self, tag, attrs):
        if self.raw_text_tag is not None:
            return
        if tag in {"script", "style", "textarea", "title", "xmp", "iframe",
                   "noembed", "noframes", "plaintext"}:
            self.raw_text_tag = tag
            return
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.destinations.append(value or "")
                    break

    def handle_endtag(self, tag):
        if tag == self.raw_text_tag and tag != "plaintext":
            self.raw_text_tag = None

    def handle_startendtag(self, tag, attrs):
        # HTML's slash does not close non-void raw-text elements.
        self.handle_starttag(tag, attrs)


def raw_html_anchor_contract_lines(content: str) -> list[str]:
    """Expose only real HTML anchors, isolated from adjacent Markdown blocks."""
    parser = _RawAnchorParser()
    parser.feed(content)
    parser.close()
    return [
        "[raw HTML anchor] <a href=\"" + escape(destination, quote=True) + "\"></a>"
        for destination in parser.destinations
    ]
