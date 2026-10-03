import unittest

from javascript_escape_sequence_decoder import decode


class TestNamedEscapes(unittest.TestCase):
    def test_newline(self):
        self.assertEqual(decode(r"\n"), "\n")

    def test_tab(self):
        self.assertEqual(decode(r"\t"), "\t")

    def test_carriage_return(self):
        self.assertEqual(decode(r"\r"), "\r")

    def test_backspace(self):
        self.assertEqual(decode(r"\b"), "\u0008")

    def test_formfeed(self):
        self.assertEqual(decode(r"\f"), "\u000c")

    def test_vertical_tab(self):
        self.assertEqual(decode(r"\v"), "\u000b")

    def test_backslash(self):
        self.assertEqual(decode(r"\\"), "\\")

    def test_single_quote(self):
        self.assertEqual(decode(r"\'"), "'")

    def test_double_quote(self):
        self.assertEqual(decode(r'\"'), '"')

    def test_backtick(self):
        self.assertEqual(decode(r"\`"), "`")

    def test_unknown_passes_through(self):
        # Per the implementation's stated behaviour, unknown escapes pass
        # through verbatim (backslash + character).
        self.assertEqual(decode(r"\z"), r"\z")


class TestUnicodeEscapes(unittest.TestCase):
    def test_basic_unicode(self):
        self.assertEqual(decode(r"\u00e9"), "é")

    def test_unicode_uppercase(self):
        self.assertEqual(decode(r"\u00E9"), "é")

    def test_unicode_cjk(self):
        self.assertEqual(decode(r"\u4e2d"), "中")

    def test_unicode_emoji(self):
        # U+1F600 is a supplementary-plane code point.
        self.assertEqual(decode(r"\u{1F600}"), "😀")

    def test_codepoint_single_digit(self):
        self.assertEqual(decode(r"\u{0}"), "\u0000")

    def test_codepoint_max(self):
        self.assertEqual(decode(r"\u{10FFFF}"), chr(0x10FFFF))

    def test_codepoint_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            decode(r"\u{110000}")


class TestHexEscapes(unittest.TestCase):
    def test_basic_hex(self):
        self.assertEqual(decode(r"\x41"), "A")

    def test_hex_lowercase(self):
        self.assertEqual(decode(r"\x6e"), "n")

    def test_hex_uppercase(self):
        self.assertEqual(decode(r"\x6E"), "n")


class TestOctalEscapes(unittest.TestCase):
    def test_single_digit(self):
        self.assertEqual(decode(r"\1"), chr(1))

    def test_two_digit(self):
        self.assertEqual(decode(r"\12"), chr(10))

    def test_three_digit(self):
        self.assertEqual(decode(r"\141"), "a")

    def test_max_octal(self):
        self.assertEqual(decode(r"\377"), chr(255))

    def test_zero(self):
        self.assertEqual(decode(r"\0"), "\u0000")


class TestMixedSequences(unittest.TestCase):
    def test_mixed_in_string(self):
        self.assertEqual(decode(r"Hello\n\u00e9\x41\141"), "Hello\néAa")

    def test_no_escapes(self):
        self.assertEqual(decode("plain text"), "plain text")

    def test_empty_string(self):
        self.assertEqual(decode(""), "")

    def test_consecutive_escapes(self):
        self.assertEqual(decode(r"\n\n\t"), "\n\n\t")

    def test_escape_at_end(self):
        self.assertEqual(decode(r"text\n"), "text\n")


class TestTypeError(unittest.TestCase):
    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            decode(123)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
