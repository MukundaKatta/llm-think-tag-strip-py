"""Tests for llm-think-tag-strip-py."""

from llm_think_tag_strip import (
    strip,
    strip_tags,
    extract_thinking,
    has_thinking,
    split_thinking,
    StripResult,
)


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


def test_strip_mixed_tags_preserve_document_order():
    # Blocks must come back in the order they appear in the text, even when
    # different default tag names are interleaved.
    text = "<reasoning>FIRST</reasoning> mid <thinking>SECOND</thinking>"
    result = strip_tags(text)
    assert result.stripped == ["FIRST", "SECOND"]
    assert result.tag_count == 2
    assert result.text == "mid"


def test_strip_does_not_match_similar_tag_names():
    # "thinking" must not match "<thinkingx>"; that tag should be left intact.
    text = "<thinkingx>keep</thinkingx>Answer."
    result = strip_tags(text)
    assert result.tag_count == 0
    assert "<thinkingx>keep</thinkingx>" in result.text


def test_has_thinking_does_not_match_similar_tag_names():
    assert has_thinking("<thinkingx>y</thinkingx>") is False


def test_strip_tag_with_attributes():
    text = '<thinking model="r1">internal</thinking>Visible.'
    result = strip_tags(text)
    assert result.tag_count == 1
    assert "internal" not in result.text
    assert "Visible." in result.text


def test_strip_empty_tag_list_strips_nothing():
    text = "<thinking>x</thinking>Hello"
    result = strip_tags(text, tags=[])
    assert result.tag_count == 0
    assert result.text == text
