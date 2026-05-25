"""llm-think-tag-strip-py — strip thinking/reasoning tags from LLM output."""

from __future__ import annotations

import re
from dataclasses import dataclass


# Common tag names used by different providers
_DEFAULT_TAGS = ["thinking", "reasoning", "scratchpad", "reflection", "thought"]


@dataclass
class StripResult:
    """Result of stripping tags from text."""

    text: str           # cleaned text
    stripped: list[str] # content that was inside tags
    tag_count: int      # number of tag blocks removed

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

    Args:
        text: The raw LLM output.
        tags: List of tag names to strip. Defaults to common thinking tag names.
        keep_newlines: If True, preserve surrounding whitespace/newlines.

    Returns:
        StripResult with cleaned text and extracted thinking blocks.

    Example::

        result = strip_tags("<thinking>Let me reason...</thinking>The answer is 42.")
        print(result.text)       # "The answer is 42."
        print(result.stripped)   # ["Let me reason..."]
        print(result.had_thinking)  # True
    """
    if tags is None:
        tags = _DEFAULT_TAGS

    stripped_blocks: list[str] = []
    cleaned = text

    for tag in tags:
        pattern = re.compile(
            rf"<{re.escape(tag)}[^>]*>(.*?)</{re.escape(tag)}>",
            re.DOTALL | re.IGNORECASE,
        )
        matches = pattern.findall(cleaned)
        stripped_blocks.extend(m.strip() for m in matches)
        cleaned = pattern.sub("", cleaned)

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
    """Return True if the text contains any thinking tags."""
    if tags is None:
        tags = _DEFAULT_TAGS
    for tag in tags:
        if re.search(rf"<{re.escape(tag)}[^>]*>", text, re.IGNORECASE):
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


__all__ = ["strip", "strip_tags", "extract_thinking", "has_thinking", "split_thinking", "StripResult"]
