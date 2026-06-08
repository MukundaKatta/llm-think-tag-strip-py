# llm-think-tag-strip-py

Strip `<thinking>`, `<reasoning>`, and other chain-of-thought tags from LLM output. Works with Claude extended thinking, Qwen, DeepSeek-R1, and others.

## Install

```bash
pip install llm-think-tag-strip-py
```

## Usage

```python
from llm_think_tag_strip import strip, strip_tags, extract_thinking, has_thinking, split_thinking

response = "<thinking>Let me reason...</thinking>The answer is 42."

# Simple strip
clean = strip(response)                  # "The answer is 42."

# Full result
result = strip_tags(response)
result.text          # "The answer is 42."
result.stripped      # ["Let me reason..."]
result.tag_count     # 1
result.had_thinking  # True

# Extract thinking without cleaning
blocks = extract_thinking(response)

# Check for thinking
if has_thinking(response):
    clean = strip(response)

# Custom tags
strip(response, tags=["reasoning", "scratchpad", "reflection"])

# Split into (thinking_blocks, clean_text)
blocks, clean = split_thinking(response)
```

Both paired tags (`<thinking>...</thinking>`) and self-closing tags
(`<thinking/>`) are removed. Matching is case-insensitive, spans multiple
lines, and ignores attributes (e.g. `<thinking model="r1">`). Tag names are
matched as whole words, so `<thinking>` is stripped while a tag such as
`<thinkingx>` is left untouched.

## API

All functions accept an optional `tags` argument — a list of tag names to
treat as thinking tags. When omitted, the default set is used:
`thinking`, `reasoning`, `scratchpad`, `reflection`, `thought`.

| Function | Returns | Description |
| --- | --- | --- |
| `strip(text, tags=None)` | `str` | Cleaned text with all thinking tags removed. |
| `strip_tags(text, tags=None, keep_newlines=False)` | `StripResult` | Full result object (see below). |
| `extract_thinking(text, tags=None)` | `list[str]` | The contents of each thinking block, in document order. |
| `has_thinking(text, tags=None)` | `bool` | `True` if the text contains any thinking tag. |
| `split_thinking(text, tags=None)` | `tuple[list[str], str]` | `(thinking_blocks, clean_text)`. |

### `StripResult`

`strip_tags()` returns a `StripResult` dataclass with these fields:

- `text: str` — the cleaned text.
- `stripped: list[str]` — the content of each removed block, in document order.
- `tag_count: int` — the number of paired tag blocks removed.
- `had_thinking: bool` — property; `True` when `tag_count > 0`.

By default `strip_tags` strips leading/trailing whitespace and collapses runs
of blank lines. Pass `keep_newlines=True` to preserve the surrounding
whitespace exactly.

All entry points raise `TypeError` when `text` is not a `str`.

This package ships a `py.typed` marker, so type checkers such as mypy and
pyright will use its inline type hints.

## Development

Run the test suite with the standard library — no third-party dependencies
required:

```bash
python3 -m unittest discover -s tests
```

## License

MIT
