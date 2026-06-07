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

## License

MIT
