# JavaScript Escape Sequence Decoder

Decodes JavaScript string escape sequences (`\u####`, `\x##`, `\u{...}`, octal, and named escape sequences) into Unicode strings.

## Usage

```python
from javascript_escape_sequence_decoder import decode

# Named escapes
print(repr(decode(r"Hello\nWorld")))  # 'Hello\nWorld'

# Unicode escapes
print(decode(r"\u00e9"))  # é
print(decode(r"\u{1F600}"))  # 😀

# Hex and octal
print(decode(r"\x41\141"))  # Aa

# Mixed
print(decode(r"Line1\n\u00e9\x41"))  # Line1\néA
```

## Why

When ingesting JSON or source files that contain JavaScript string literals, escape sequences often arrive as raw backslash-prefixed text rather than decoded characters. Python's own codecs do not cover the full JavaScript grammar (code point braces, legacy octals, the specific named set). This library fills that gap with a single pure-Python function and no third-party dependencies.

## Edge Cases

- **Unknown escapes** like `\z` pass through verbatim (`\z`). This matches non-strict JavaScript string literal behaviour. If you need strict rejection of unknown escapes, post-process the result.
- **Legacy octal escapes** (`\1` to `\377`) are supported and map to Latin-1 code points, matching how browsers treat them in non-strict mode.
- **Out-of-range code points** (`\u{110000}`) raise `ValueError`. The maximum valid code point is `U+10FFFF`.
- The decoder operates on the full string at once. It is not a streaming parser; very large inputs are processed in memory.
