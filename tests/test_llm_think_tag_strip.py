"""Tests for llm-think-tag-strip-py."""
import pytest
from llm_think_tag_strip import strip, strip_tags, extract_thinking, has_thinking, split_thinking, StripResult


def test_strip_basic():
    text = "<thinking>Let me think...</thinking>The answer is 42."
    result = strip(text)
    assert "thinking" not in result.lower()
    assert "Let me think" not in result
    assert "42" in result


def test_strip_tags_returns_struct():
    text = "<thinking>Some reasoning</thinking>Final answer."
    result = strip_tags(text)
    assert isinstance(result, StripResult)
    assert result.tag_count == 1
    assert "Some reasoning" in result.stripped[0]
    assert "Final answer" in result.text
    assert result.had_thinking is True


def test_strip_tags_no_thinking():
    text = "Just a plain response."
    result = strip_tags(text)
    assert result.tag_count == 0
    assert result.had_thinking is False
    assert result.stripped == []
    assert result.text == text


def test_strip_multiple_blocks():
    text = "<thinking>First thought</thinking>Middle.<thinking>Second thought</thinking>End."
    result = strip_tags(text)
    assert result.tag_count == 2
    assert "First thought" in result.stripped[0]
    assert "Second thought" in result.stripped[1]
    assert "Middle" in result.text
    assert "End" in result.text


def test_strip_reasoning_tag():
    text = "<reasoning>My reasoning here</reasoning>Result: done."
    result = strip_tags(text, tags=["reasoning"])
    assert result.tag_count == 1
    assert "Result: done" in result.text


def test_strip_custom_tags():
    text = "<scratchpad>notes</scratchpad>Answer."
    result = strip_tags(text, tags=["scratchpad"])
    assert result.tag_count == 1
    assert "Answer" in result.text


def test_strip_multiline_content():
    text = "<thinking>\nLine one\nLine two\n</thinking>Final."
    result = strip_tags(text)
    assert result.tag_count == 1
    assert "Final" in result.text
    assert "Line one" not in result.text


def test_strip_preserves_non_tag_content():
    text = "<thinking>ignore me</thinking>Keep this: **bold** text."
    result = strip_tags(text)
    assert "Keep this" in result.text
    assert "**bold**" in result.text


def test_strip_case_insensitive():
    text = "<THINKING>caps tag</THINKING>Answer."
    result = strip_tags(text)
    assert result.tag_count == 1
    assert "Answer" in result.text


def test_extract_thinking():
    text = "<thinking>reason A</thinking>Some text.<thinking>reason B</thinking>"
    blocks = extract_thinking(text)
    assert len(blocks) == 2
    assert "reason A" in blocks[0]
    assert "reason B" in blocks[1]


def test_extract_thinking_empty():
    assert extract_thinking("No tags here.") == []


def test_has_thinking_true():
    assert has_thinking("<thinking>yes</thinking>") is True


def test_has_thinking_false():
    assert has_thinking("plain text") is False


def test_has_thinking_custom_tag():
    assert has_thinking("<scratchpad>x</scratchpad>", tags=["scratchpad"]) is True
    assert has_thinking("<thinking>x</thinking>", tags=["scratchpad"]) is False


def test_split_thinking():
    text = "<thinking>reason</thinking>Answer."
    blocks, clean = split_thinking(text)
    assert "reason" in blocks[0]
    assert "Answer" in clean
    assert "thinking" not in clean.lower()


def test_strip_result_had_thinking():
    result = strip_tags("no tags")
    assert result.had_thinking is False
    result2 = strip_tags("<thinking>x</thinking>")
    assert result2.had_thinking is True


def test_strip_keeps_whitespace_option():
    text = "<thinking>think</thinking>\n\nAnswer."
    result = strip_tags(text, keep_newlines=True)
    assert "Answer" in result.text
