"""llm-think-tag-strip-py — strip thinking/reasoning tags from LLM output."""

from __future__ import annotations

import re
from dataclasses import dataclass


# Common tag names used by different providers
_DEFAULT_TAGS = ["thinking", "reasoning", "scratchpad", "reflection", "thought"]


@dataclass
class StripResult:
    """Result of stripping tags from text."""

    text: str  # cleaned text
    stripped: list[str]  # content that was inside tags
    tag_count: int  # number of tag blocks removed

    @property
    def had_thinking(self) -> bool:
        return self.tag_count > 0


def strip_tags(
    text: str,
    tags: list[str] | None = None,
    keep_newlines: bool = False,
) -> StripResult:
    """
    Remove XML-style thinking/reasoning tags and their content from text.

    Both paired tags (``<thinking>...</thinking>``) and self-closing tags
    (``<thinking/>``) are removed. Self-closing tags carry no content, so they
    do not contribute an entry to ``stripped`` or to ``tag_count``.

    Args:
        text: The raw LLM output.
        tags: List of tag names to strip. Defaults to common thinking tag names.
        keep_newlines: If True, preserve surrounding whitespace/newlines.

    Returns:
        StripResult with cleaned text and extracted thinking blocks.

    Raises:
        TypeError: If ``text`` is not a ``str``.

    Example::

        result = strip_tags("<thinking>Let me reason...</thinking>The answer is 42.")
        print(result.text)       # "The answer is 42."
        print(result.stripped)   # ["Let me reason..."]
        print(result.had_thinking)  # True
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")

    if tags is None:
        tags = _DEFAULT_TAGS

    stripped_blocks: list[str] = []
    cleaned = text

    if tags:
        # Match any of the given tags in a single pass so that the extracted
        # blocks are returned in document order (not grouped by tag name).
        # The trailing (?=[\s/>]) ensures we only match whole tag names, so
        # ``thinking`` does not also match ``<thinkingx>``.
        names = "|".join(re.escape(tag) for tag in tags)
        pattern = re.compile(
            rf"<(?:{names})(?=[\s/>])[^>]*>(.*?)</(?:{names})\s*>",
            re.DOTALL | re.IGNORECASE,
        )
        stripped_blocks = [m.strip() for m in pattern.findall(cleaned)]
        cleaned = pattern.sub("", cleaned)

        # Self-closing tags (e.g. ``<thinking/>``) carry no content but are
        # still detected by ``has_thinking``. Remove them too so that ``strip``
        # and ``has_thinking`` stay consistent.
        self_closing = re.compile(
            rf"<(?:{names})(?=[\s/>])[^>]*/\s*>",
            re.IGNORECASE,
        )
        cleaned = self_closing.sub("", cleaned)

    if not keep_newlines:
        # Collapse multiple blank lines into at most one
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()

    return StripResult(
        text=cleaned,
        stripped=stripped_blocks,
        tag_count=len(stripped_blocks),
    )


def strip(text: str, tags: list[str] | None = None) -> str:
    """Strip thinking tags and return the cleaned text only."""
    return strip_tags(text, tags=tags).text


def extract_thinking(text: str, tags: list[str] | None = None) -> list[str]:
    """Extract and return the thinking block contents without cleaning the text."""
    result = strip_tags(text, tags=tags)
    return result.stripped


def has_thinking(text: str, tags: list[str] | None = None) -> bool:
    """Return True if the text contains any thinking tags.

    Raises:
        TypeError: If ``text`` is not a ``str``.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    if tags is None:
        tags = _DEFAULT_TAGS
    for tag in tags:
        if re.search(rf"<{re.escape(tag)}(?=[\s/>])[^>]*>", text, re.IGNORECASE):
            return True
    return False


def split_thinking(text: str, tags: list[str] | None = None) -> tuple[list[str], str]:
    """
    Split text into (thinking_blocks, clean_text).

    Returns:
        (list of thinking block strings, cleaned text without tags)
    """
    result = strip_tags(text, tags=tags)
    return result.stripped, result.text


__all__ = [
    "strip",
    "strip_tags",
    "extract_thinking",
    "has_thinking",
    "split_thinking",
    "StripResult",
]
