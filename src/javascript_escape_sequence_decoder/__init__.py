"""JavaScript Escape Sequence Decoder.

Decodes JavaScript string escape sequences (\\u####, \\x##, \\u{...}, octal,
and named escape sequences) into Unicode strings.
"""

from javascript_escape_sequence_decoder.core import decode

__all__ = ["decode"]
