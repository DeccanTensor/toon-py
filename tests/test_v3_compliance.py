"""
TOON v3.0 Specification Compliance Tests for deccan-toon.

These tests verify that the implementation correctly handles all edge cases
defined in the official TOON v3.0 specification.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon


@pytest.mark.compliance
class TestTypeInference:
    """TOON v3.0: Type inference for literals must be case-sensitive and strict."""

    def test_bool_true_lowercase(self) -> None:
        """'true' (lowercase) should decode to Python True."""
        data = [{"flag": True}]
        encoded = deccan_toon.dumps(data)
        assert "true" in encoded
        assert deccan_toon.loads(encoded) == data

    def test_bool_false_lowercase(self) -> None:
        """'false' (lowercase) should decode to Python False."""
        data = [{"flag": False}]
        encoded = deccan_toon.dumps(data)
        assert "false" in encoded
        assert deccan_toon.loads(encoded) == data

    def test_null_literal(self) -> None:
        """'null' should decode to Python None."""
        data = [{"value": None}]
        encoded = deccan_toon.dumps(data)
        assert "null" in encoded
        assert deccan_toon.loads(encoded) == data

    def test_integer_positive(self) -> None:
        """Positive integers should round-trip correctly."""
        data = [{"x": 42}]
        assert deccan_toon.loads(deccan_toon.dumps(data)) == data

    def test_integer_negative(self) -> None:
        """Negative integers should round-trip correctly."""
        data = [{"x": -999}]
        assert deccan_toon.loads(deccan_toon.dumps(data)) == data

    def test_float_with_decimal(self) -> None:
        """Floats with decimals should round-trip correctly."""
        data = [{"pi": 3.14159}]
        assert deccan_toon.loads(deccan_toon.dumps(data)) == data

    def test_float_scientific_notation(self) -> None:
        """Scientific notation floats should round-trip correctly."""
        data = [{"big": 1e20}]
        result = deccan_toon.loads(deccan_toon.dumps(data))
        assert result[0]["big"] == pytest.approx(1e20)


@pytest.mark.compliance
class TestAmbiguousStringQuoting:
    """TOON v3.0: Strings that look like literals MUST be quoted."""

    def test_string_true_is_quoted_and_stays_string(self) -> None:
        """String 'true' must not become boolean True."""
        data = [{"word": "true"}]
        encoded = deccan_toon.dumps(data)
        # Must be quoted in output
        assert '"true"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["word"], str)

    def test_string_false_is_quoted_and_stays_string(self) -> None:
        """String 'false' must not become boolean False."""
        data = [{"word": "false"}]
        encoded = deccan_toon.dumps(data)
        assert '"false"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["word"], str)

    def test_string_null_is_quoted_and_stays_string(self) -> None:
        """String 'null' must not become None."""
        data = [{"word": "null"}]
        encoded = deccan_toon.dumps(data)
        assert '"null"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["word"], str)

    def test_string_integer_is_quoted_and_stays_string(self) -> None:
        """String '123' must not become integer 123."""
        data = [{"code": "123"}]
        encoded = deccan_toon.dumps(data)
        assert '"123"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["code"], str)

    def test_string_negative_integer_is_quoted(self) -> None:
        """String '-42' must not become integer -42."""
        data = [{"code": "-42"}]
        encoded = deccan_toon.dumps(data)
        assert '"-42"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["code"], str)

    def test_string_float_is_quoted_and_stays_string(self) -> None:
        """String '3.14' must not become float 3.14."""
        data = [{"version": "3.14"}]
        encoded = deccan_toon.dumps(data)
        assert '"3.14"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert isinstance(decoded[0]["version"], str)

    def test_empty_string_is_quoted(self) -> None:
        """Empty string '' must be quoted to avoid ambiguity."""
        data = [{"empty": ""}]
        encoded = deccan_toon.dumps(data)
        assert '""' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data
        assert decoded[0]["empty"] == ""


@pytest.mark.compliance
class TestSpecialCharacterQuoting:
    """TOON v3.0: Strings with special chars must be quoted and escaped."""

    def test_string_with_colon(self) -> None:
        """Strings containing ':' must be quoted."""
        data = [{"time": "12:30:45"}]
        encoded = deccan_toon.dumps(data)
        assert '"12:30:45"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_comma(self) -> None:
        """Strings containing ',' must be quoted."""
        data = [{"list": "a,b,c"}]
        encoded = deccan_toon.dumps(data)
        assert '"a,b,c"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_brackets(self) -> None:
        """Strings containing '[' or ']' must be quoted."""
        data = [{"array_like": "[not an array]"}]
        encoded = deccan_toon.dumps(data)
        assert '"[not an array]"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_braces(self) -> None:
        """Strings containing '{' or '}' must be quoted."""
        data = [{"object_like": "{not an object}"}]
        encoded = deccan_toon.dumps(data)
        assert '"{not an object}"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_backslash(self) -> None:
        """Strings containing '\\' must be quoted and escaped."""
        data = [{"path": "C:\\Users\\test"}]
        encoded = deccan_toon.dumps(data)
        # JSON escaping: backslash becomes \\
        assert "C:\\\\Users\\\\test" in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_newline(self) -> None:
        """Strings containing newlines must be quoted and escaped."""
        data = [{"text": "line1\nline2"}]
        encoded = deccan_toon.dumps(data)
        assert "\\n" in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_tab(self) -> None:
        """Strings containing tabs must be quoted and escaped."""
        data = [{"text": "col1\tcol2"}]
        encoded = deccan_toon.dumps(data)
        assert "\\t" in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_carriage_return(self) -> None:
        """Strings containing carriage returns must be quoted and escaped."""
        data = [{"text": "line1\r\nline2"}]
        encoded = deccan_toon.dumps(data)
        assert "\\r" in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_string_with_double_quote(self) -> None:
        """Strings containing double quotes must be quoted and escaped."""
        data = [{"speech": 'He said "hello"'}]
        encoded = deccan_toon.dumps(data)
        assert '\\"' in encoded
        decoded = deccan_toon.loads(encoded)
        assert decoded == data


@pytest.mark.compliance
class TestPlainStrings:
    """TOON v3.0: Safe strings should remain unquoted for readability."""

    def test_simple_word_not_quoted(self) -> None:
        """Simple alphanumeric strings should not be quoted."""
        data = [{"name": "Alice"}]
        encoded = deccan_toon.dumps(data)
        # Should appear without quotes
        lines = encoded.strip().split("\n")
        assert "Alice" in lines[1]
        assert '"Alice"' not in lines[1]
        decoded = deccan_toon.loads(encoded)
        assert decoded == data

    def test_words_with_spaces_not_quoted(self) -> None:
        """Strings with spaces (but no special chars) may remain unquoted."""
        data = [{"name": "New York"}]
        encoded = deccan_toon.dumps(data)
        decoded = deccan_toon.loads(encoded)
        assert decoded == data


@pytest.mark.compliance
class TestNoCommentSupport:
    """TOON v3.0: Comments are NOT supported - '#' is data."""

    def test_hash_in_string_preserved(self) -> None:
        """'#' character in strings must be preserved as data."""
        data = [{"tag": "#trending"}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data
        assert decoded[0]["tag"] == "#trending"

    def test_hash_only_value(self) -> None:
        """A value of '#' alone is preserved."""
        data = [{"symbol": "#"}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data


@pytest.mark.compliance
class TestSparseArrays:
    """TOON v3.0: Missing columns should use explicit null."""

    def test_missing_key_becomes_null(self) -> None:
        """Rows missing a key should encode that column as null."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2},  # missing 'name'
        ]
        encoded = deccan_toon.dumps(data)
        decoded = deccan_toon.loads(encoded)
        assert decoded[0] == {"id": 1, "name": "Alice"}
        assert decoded[1] == {"id": 2, "name": None}


@pytest.mark.compliance
class TestNestedStructures:
    """TOON v3.0: Nested objects and arrays via inline JSON."""

    def test_nested_dict_round_trip(self) -> None:
        """Nested dictionaries should round-trip correctly."""
        data = [{"meta": {"x": 10, "y": 20}}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data
        assert isinstance(decoded[0]["meta"], dict)

    def test_nested_list_round_trip(self) -> None:
        """Nested lists should round-trip correctly."""
        data = [{"tags": ["a", "b", "c"]}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data
        assert isinstance(decoded[0]["tags"], list)

    def test_nested_matrix_round_trip(self) -> None:
        """Nested matrix (list of lists) should round-trip correctly."""
        data = [{"matrix": [[1, 2], [3, 4]]}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data

    def test_deeply_nested_structure(self) -> None:
        """Deeply nested structures should round-trip correctly."""
        data = [{"deep": {"level1": {"level2": {"level3": "bottom"}}}}]
        decoded = deccan_toon.loads(deccan_toon.dumps(data))
        assert decoded == data


@pytest.mark.compliance
class TestHeaderFormat:
    """TOON v3.0: Header format compliance."""

    def test_header_contains_count(self) -> None:
        """Header should include accurate row count."""
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        encoded = deccan_toon.dumps(data)
        assert "items[3]" in encoded

    def test_header_contains_columns(self) -> None:
        """Header should list column names in braces."""
        data = [{"id": 1, "name": "test"}]
        encoded = deccan_toon.dumps(data)
        assert "{id,name}" in encoded or "{name,id}" in encoded

    def test_header_ends_with_colon(self) -> None:
        """Header line should end with colon."""
        data = [{"x": 1}]
        encoded = deccan_toon.dumps(data)
        first_line = encoded.split("\n")[0]
        assert first_line.endswith(":")


@pytest.mark.compliance
class TestRowWidthValidation:
    """TOON v3.0: Row width must match header."""

    def test_row_width_mismatch_raises_error(self) -> None:
        """Decoder should raise error if row has wrong number of columns."""
        payload = "items[1]{a,b,c}:\n  1, 2"  # only 2 values for 3 columns
        with pytest.raises(deccan_toon.TOONDecodeError):
            deccan_toon.loads(payload)

    def test_extra_columns_raises_error(self) -> None:
        """Decoder should raise error if row has extra columns."""
        payload = "items[1]{a,b}:\n  1, 2, 3, 4"  # 4 values for 2 columns
        with pytest.raises(deccan_toon.TOONDecodeError):
            deccan_toon.loads(payload)
