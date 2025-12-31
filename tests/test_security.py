import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon  # noqa: E402


ALLOWED_ERRORS = (ValueError, getattr(deccan_toon, "TOONDecodeError", ValueError))


def test_malformed_header_cut_off() -> None:
    payload = "items[2]{id,"
    with pytest.raises(ALLOWED_ERRORS):
        deccan_toon.loads(payload)


def test_row_mismatch_header_3_row_5() -> None:
    payload = "items[1]{a,b,c}:\n  1,2,3,4,5"
    with pytest.raises(ALLOWED_ERRORS):
        deccan_toon.loads(payload)


def test_type_attack_no_python_object_injection_executes() -> None:
    # Not a crash test (we can't "prove" no exec), but we can ensure decoding is safe
    # and doesn't blow up on scary-looking strings.
    payload = 'items[1]{x}:\n  __import__("os").system("echo pwned")'
    out = deccan_toon.loads(payload)
    assert out == [{"x": '__import__("os").system("echo pwned")'}]


def test_type_attack_invalid_json_string_raises_clean_error() -> None:
    # JSON does not allow raw control chars in strings.
    payload = 'items[1]{s}:\n  "bad\x00string"'
    with pytest.raises(ALLOWED_ERRORS):
        deccan_toon.loads(payload)


def test_type_attack_unexpected_row_quotes_raise_clean_error() -> None:
    # Unterminated quoted field should not crash.
    payload = 'items[1]{s}:\n  "unterminated'
    with pytest.raises(ALLOWED_ERRORS):
        deccan_toon.loads(payload)

