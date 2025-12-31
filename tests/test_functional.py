import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon


@pytest.mark.unit
def test_round_trip_standard_inputs() -> None:
    data = [{"id": 1, "name": "Pune"}, {"id": 2, "name": "Mumbai"}]
    assert deccan_toon.loads(deccan_toon.dumps(data)) == data


@pytest.mark.unit
@pytest.mark.parametrize(
    "value,expected_type",
    [
        (123, int),
        (-7, int),
        (None, type(None)),
        (True, bool),
        (False, bool),
    ],
)
def test_type_fidelity(value, expected_type) -> None:
    data = [{"x": value}]
    out = deccan_toon.loads(deccan_toon.dumps(data))
    assert len(out) == 1
    assert out[0]["x"] == value
    assert type(out[0]["x"]) is expected_type


@pytest.mark.unit
def test_quote_handling_commas_newlines_quotes() -> None:
    tricky = 'hello, world\nand then he said "wow"'
    data = [{"id": 1, "text": tricky}]
    encoded = deccan_toon.dumps(data)
    decoded = deccan_toon.loads(encoded)
    assert decoded == data
