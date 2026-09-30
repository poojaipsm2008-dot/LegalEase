"""Text cleanup and document structure helpers."""

import re
import unicodedata


def sanitize_text(text: str) -> str:
    """Normalize unsafe controls while preserving meaningful Unicode and punctuation."""
    normalized = unicodedata.normalize("NFC", text or "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(
        char for char in normalized
        if char in "\n\t" or unicodedata.category(char) not in {"Cc", "Cf"}
    ).strip()


def split_clauses(text: str) -> list[str]:
    """Split semicolon separated terms without discarding any nonempty clause."""
    return [part.strip() for part in sanitize_text(text).split(";") if part.strip()]


def parse_document(text: str) -> list[tuple[str, str]]:
    """Return (kind, content) blocks for headings, lists, and paragraphs."""
    blocks: list[tuple[str, str]] = []
    for line in sanitize_text(text).splitlines():
        value = line.strip()
        if not value:
            if blocks and blocks[-1][0] != "blank":
                blocks.append(("blank", ""))
        elif value.startswith("### "):
            blocks.append(("heading2", value[4:].strip()))
        elif value.startswith("## "):
            blocks.append(("heading2", value[3:].strip()))
        elif value.startswith("# "):
            blocks.append(("title", value[2:].strip()))
        elif re.match(r"^(?:[-*•]|\d+[.)])\s+", value):
            blocks.append(("list", re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", value)))
        elif value.isupper() and len(value) < 100:
            blocks.append(("heading2", value.title()))
        else:
            blocks.append(("paragraph", value))
    return blocks
