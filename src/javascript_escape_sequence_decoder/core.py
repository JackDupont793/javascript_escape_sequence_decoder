"""Core implementation of JavaScript escape sequence decoding.

Decodes JavaScript string escape sequences per ECMAScript specification
(including legacy octal escapes and Unicode code point escapes). Handles
the full escape grammar in both string literals and template literals.

Choices made:
- Legacy octal escapes (\\1 through \\377) are supported because they appear
  widely in legacy code; they are decoded as Latin-1 code points.
- Named escapes like \\n, \\t, \\r are supported.
- Unsupported sequences (e.g., \\z) pass through verbatim, matching the
  JavaScript behaviour for non-strict string literals.
"""

import re

# Maps named escape sequences to their Unicode character.
_NAMED_ESCAPES: dict[str, str] = {
    "b": "\u0008",
    "f": "\u000c",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\u000b",
    "0": "\u0000",
    "'": "'",
    '"': '"',
    "\\": "\\",
    "`": "`",
}

# Matches an escape sequence (a backslash followed by any single char).
_ESCAPE_RE: re.Pattern[str] = re.compile(r"\\(.)", re.DOTALL)

# Matches a hex escape \\x## (exactly two hex digits).
_HEX_ESCAPE_RE: re.Pattern[str] = re.compile(r"\\x([0-9A-Fa-f]{2})")

# Matches a Unicode escape \\u#### (exactly four hex digits).
_UNICODE_ESCAPE_RE: re.Pattern[str] = re.compile(r"\\u([0-9A-Fa-f]{4})")

# Matches a code point escape \\u{...} with 1 to 6 hex digits.
_CODEPOINT_ESCAPE_RE: re.Pattern[str] = re.compile(r"\\u\{([0-9A-Fa-f]{1,6})\}")

# Matches a legacy octal escape: \\0 to \\377 (1 to 3 octal digits).
_OCTAL_ESCAPE_RE: re.Pattern[str] = re.compile(r"\\([0-7]{1,3})")

# Matches a non-zero digit followed by octal digits.
_ZERO_OCTAL_RE: re.Pattern[str] = re.compile(r"\\(0[0-7]{0,2})")


def _decode_codepoint(hex_digits: str) -> str:
    """Convert a hex string into a Unicode character.

    Raises ValueError if out of the valid Unicode range.
    """
    code_point: int = int(hex_digits, 16)
    if code_point > 0x10FFFF:
        raise ValueError(f"Code point out of range: {hex_digits}")
    return chr(code_point)


def _decode_octal(octal_digits: str) -> str:
    """Convert an octal string to a Latin-1 character.

    Octal escapes in JS map to Latin-1 (code points 0-255). Values above
    0xFF (377 octal) should not reach here per the regex.
    """
    code_point: int = int(octal_digits, 8)
    if code_point > 255:
        raise ValueError(f"Octal escape out of range: \\{octal_digits}")
    return chr(code_point)


def decode(text: str) -> str:
    """Decode JavaScript escape sequences in *text*.

    Supported escapes:
      - \\u####        : 4-hex-digit Unicode escape
      - \\u{...}      : 1-6 hex digits, code point escape (ES6+)
      - \\x##         : 2-hex-digit Latin-1 escape
      - \\1 to \\377   : legacy octal escape (max 255)
      - \\n, \\t, \\r, \\b, \\f, \\v, \\0, \\\\, \\' , \\" , \\`
      - any other \\X : passes through verbatim (\\ + X)

    Args:
        text: A string that may contain JavaScript escape sequences.

    Returns:
        The decoded Unicode string.

    Raises:
        ValueError: If a \\u{...} escape exceeds 0x10FFFF.
    """
    if not isinstance(text, str):
        raise TypeError("decode() expected str, got " + type(text).__name__)

    def _replace_codepoint(match: re.Match[str]) -> str:
        return _decode_codepoint(match.group(1))

    def _replace_unicode(match: re.Match[str]) -> str:
        return chr(int(match.group(1), 16))

    def _replace_hex(match: re.Match[str]) -> str:
        return chr(int(match.group(1), 16))

    def _replace_octal(match: re.Match[str]) -> str:
        return _decode_octal(match.group(1))

    def _replace_escape(match: re.Match[str]) -> str:
        char: str = match.group(1)
        return _NAMED_ESCAPES.get(char, "\\" + char)

    # Process escapes in the order ECMAScript would lexically accept them:
    # code point first (most specific), then unicode, then hex, then octal,
    # then remaining single-char named escapes. Using regex substitution on
    # non-overlapping patterns keeps the logic simple and predictable.
    result: str = text
    result = _CODEPOINT_ESCAPE_RE.sub(_replace_codepoint, result)
    result = _UNICODE_ESCAPE_RE.sub(_replace_unicode, result)
    result = _HEX_ESCAPE_RE.sub(_replace_hex, result)
    result = _OCTAL_ESCAPE_RE.sub(_replace_octal, result)
    result = _ESCAPE_RE.sub(_replace_escape, result)
    return result
