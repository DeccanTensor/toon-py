import os
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon

ALLOWED_ERRORS: tuple[type[Exception], ...] = (
    ValueError,
    getattr(deccan_toon, "TOONDecodeError", ValueError),
)


def _jsonish_scalars():
    # Include NaN/Inf; round-trip equality isn't required for fuzz (just no crashes).
    return st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-10**200, max_value=10**200),
        st.floats(allow_nan=True, allow_infinity=True, width=64),
        st.text(),
    )


JSONISH = st.recursive(
    _jsonish_scalars(),
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(), children, max_size=5),
    ),
    max_leaves=25,
)


KEY = st.text(
    alphabet=st.characters(
        whitelist_categories=("Ll", "Lu", "Nd"),
        whitelist_characters="_",
        min_codepoint=48,
        max_codepoint=122,
    ),
    min_size=1,
    max_size=10,
).filter(lambda s: ("," not in s and "\n" not in s and "{" not in s and "}" not in s))


@st.composite
def list_of_dicts_same_keys(draw):
    keys = draw(st.lists(KEY, min_size=1, max_size=5, unique=True))
    rows = draw(st.integers(min_value=0, max_value=30))
    return [
        {k: draw(JSONISH) for k in keys}
        for _ in range(rows)
    ]


@pytest.mark.fuzz
@settings(
    max_examples=2000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(data=list_of_dicts_same_keys())
def test_fuzz_no_unhandled_exception(data) -> None:
    try:
        toon = deccan_toon.dumps(data)
    except Exception as e:
        pytest.fail(f"Unhandled exception in dumps: {type(e).__name__}: {e}")

    try:
        _ = deccan_toon.loads(toon)
    except ALLOWED_ERRORS:
        # Clean failure is acceptable; the key property is "no crash".
        return
    except Exception as e:
        pytest.fail(f"Unhandled exception in loads: {type(e).__name__}: {e}")
