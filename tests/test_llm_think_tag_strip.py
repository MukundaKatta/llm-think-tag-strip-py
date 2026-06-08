"""Tests for llm-think-tag-strip-py.

These tests use only the Python standard library ``unittest`` framework so
they can be run without any third-party dependencies::

    python3 -m unittest discover -s tests
"""

import unittest

from llm_think_tag_strip import (
    StripResult,
    extract_thinking,
    has_thinking,
    split_thinking,
    strip,
    strip_tags,
)


class StripTests(unittest.TestCase):
    def test_strip_basic(self):
        text = "<thinking>Let me think...</thinking>The answer is 42."
        result = strip(text)
        self.assertNotIn("thinking", result.lower())
        self.assertNotIn("Let me think", result)
        self.assertIn("42", result)

    def test_strip_tags_returns_struct(self):
        text = "<thinking>Some reasoning</thinking>Final answer."
        result = strip_tags(text)
        self.assertIsInstance(result, StripResult)
        self.assertEqual(result.tag_count, 1)
        self.assertIn("Some reasoning", result.stripped[0])
        self.assertIn("Final answer", result.text)
        self.assertTrue(result.had_thinking)

    def test_strip_tags_no_thinking(self):
        text = "Just a plain response."
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 0)
        self.assertFalse(result.had_thinking)
        self.assertEqual(result.stripped, [])
        self.assertEqual(result.text, text)

    def test_strip_multiple_blocks(self):
        text = (
            "<thinking>First thought</thinking>Middle."
            "<thinking>Second thought</thinking>End."
        )
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 2)
        self.assertIn("First thought", result.stripped[0])
        self.assertIn("Second thought", result.stripped[1])
        self.assertIn("Middle", result.text)
        self.assertIn("End", result.text)

    def test_strip_reasoning_tag(self):
        text = "<reasoning>My reasoning here</reasoning>Result: done."
        result = strip_tags(text, tags=["reasoning"])
        self.assertEqual(result.tag_count, 1)
        self.assertIn("Result: done", result.text)

    def test_strip_custom_tags(self):
        text = "<scratchpad>notes</scratchpad>Answer."
        result = strip_tags(text, tags=["scratchpad"])
        self.assertEqual(result.tag_count, 1)
        self.assertIn("Answer", result.text)

    def test_strip_multiline_content(self):
        text = "<thinking>\nLine one\nLine two\n</thinking>Final."
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 1)
        self.assertIn("Final", result.text)
        self.assertNotIn("Line one", result.text)

    def test_strip_preserves_non_tag_content(self):
        text = "<thinking>ignore me</thinking>Keep this: **bold** text."
        result = strip_tags(text)
        self.assertIn("Keep this", result.text)
        self.assertIn("**bold**", result.text)

    def test_strip_case_insensitive(self):
        text = "<THINKING>caps tag</THINKING>Answer."
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 1)
        self.assertIn("Answer", result.text)

    def test_strip_keeps_whitespace_option(self):
        text = "<thinking>think</thinking>\n\nAnswer."
        result = strip_tags(text, keep_newlines=True)
        self.assertIn("Answer", result.text)
        # With keep_newlines the surrounding blank lines are preserved.
        self.assertTrue(result.text.startswith("\n\n"))

    def test_strip_default_collapses_blank_lines(self):
        text = "<thinking>x</thinking>\n\n\n\nAnswer."
        result = strip_tags(text)
        self.assertEqual(result.text, "Answer.")

    def test_strip_mixed_tags_preserve_document_order(self):
        # Blocks must come back in the order they appear in the text, even when
        # different default tag names are interleaved.
        text = "<reasoning>FIRST</reasoning> mid <thinking>SECOND</thinking>"
        result = strip_tags(text)
        self.assertEqual(result.stripped, ["FIRST", "SECOND"])
        self.assertEqual(result.tag_count, 2)
        self.assertEqual(result.text, "mid")

    def test_strip_does_not_match_similar_tag_names(self):
        # "thinking" must not match "<thinkingx>"; that tag should be left intact.
        text = "<thinkingx>keep</thinkingx>Answer."
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 0)
        self.assertIn("<thinkingx>keep</thinkingx>", result.text)

    def test_strip_tag_with_attributes(self):
        text = '<thinking model="r1">internal</thinking>Visible.'
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 1)
        self.assertNotIn("internal", result.text)
        self.assertIn("Visible.", result.text)

    def test_strip_empty_tag_list_strips_nothing(self):
        text = "<thinking>x</thinking>Hello"
        result = strip_tags(text, tags=[])
        self.assertEqual(result.tag_count, 0)
        self.assertEqual(result.text, text)

    def test_strip_unclosed_tag_left_intact(self):
        # An unclosed tag is not a complete block and is left untouched.
        text = "<thinking>no close"
        result = strip_tags(text)
        self.assertEqual(result.tag_count, 0)
        self.assertEqual(result.text, "<thinking>no close")


class SelfClosingTagTests(unittest.TestCase):
    """Regression tests: self-closing tags must be removed by ``strip`` so it
    stays consistent with ``has_thinking``."""

    def test_self_closing_removed(self):
        self.assertEqual(strip("<thinking/>Answer"), "Answer")

    def test_self_closing_with_space_removed(self):
        self.assertEqual(strip("<thinking />Answer"), "Answer")

    def test_self_closing_custom_default_tag(self):
        self.assertEqual(strip("<reasoning/>X"), "X")

    def test_self_closing_consistent_with_has_thinking(self):
        text = "<thinking/>Answer"
        self.assertTrue(has_thinking(text))
        self.assertNotIn("thinking", strip(text).lower())

    def test_self_closing_adds_no_block(self):
        result = strip_tags("<thinking/>Answer")
        self.assertEqual(result.stripped, [])
        self.assertEqual(result.tag_count, 0)
        self.assertEqual(result.text, "Answer")


class ExtractThinkingTests(unittest.TestCase):
    def test_extract_thinking(self):
        text = "<thinking>reason A</thinking>Some text.<thinking>reason B</thinking>"
        blocks = extract_thinking(text)
        self.assertEqual(len(blocks), 2)
        self.assertIn("reason A", blocks[0])
        self.assertIn("reason B", blocks[1])

    def test_extract_thinking_empty(self):
        self.assertEqual(extract_thinking("No tags here."), [])


class HasThinkingTests(unittest.TestCase):
    def test_has_thinking_true(self):
        self.assertTrue(has_thinking("<thinking>yes</thinking>"))

    def test_has_thinking_false(self):
        self.assertFalse(has_thinking("plain text"))

    def test_has_thinking_custom_tag(self):
        self.assertTrue(has_thinking("<scratchpad>x</scratchpad>", tags=["scratchpad"]))
        self.assertFalse(has_thinking("<thinking>x</thinking>", tags=["scratchpad"]))

    def test_has_thinking_does_not_match_similar_tag_names(self):
        self.assertFalse(has_thinking("<thinkingx>y</thinkingx>"))

    def test_has_thinking_self_closing(self):
        self.assertTrue(has_thinking("<thinking/>"))


class SplitThinkingTests(unittest.TestCase):
    def test_split_thinking(self):
        text = "<thinking>reason</thinking>Answer."
        blocks, clean = split_thinking(text)
        self.assertIn("reason", blocks[0])
        self.assertIn("Answer", clean)
        self.assertNotIn("thinking", clean.lower())


class StripResultTests(unittest.TestCase):
    def test_strip_result_had_thinking(self):
        result = strip_tags("no tags")
        self.assertFalse(result.had_thinking)
        result2 = strip_tags("<thinking>x</thinking>")
        self.assertTrue(result2.had_thinking)


class TypeValidationTests(unittest.TestCase):
    """``strip_tags`` and ``has_thinking`` should raise a clear ``TypeError``
    on non-string input rather than leaking a low-level regex error."""

    def test_strip_tags_rejects_none(self):
        with self.assertRaises(TypeError):
            strip_tags(None)  # type: ignore[arg-type]

    def test_strip_rejects_int(self):
        with self.assertRaises(TypeError):
            strip(123)  # type: ignore[arg-type]

    def test_has_thinking_rejects_none(self):
        with self.assertRaises(TypeError):
            has_thinking(None)  # type: ignore[arg-type]

    def test_extract_thinking_rejects_bytes(self):
        with self.assertRaises(TypeError):
            extract_thinking(b"bytes")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
