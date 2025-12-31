import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon  # noqa: E402


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _fixtures_dir() -> Path:
    return _repo_root() / "tests" / "testdata" / "fixtures"


def _read_fixture(name: str) -> str:
    path = _fixtures_dir() / name
    if not path.exists():
        pytest.skip(
            f"Missing fixture {name}. Ensure test fixtures exist under tests/testdata/fixtures/."
        )
    return path.read_text(encoding="utf-8")


def test_fixture_syntax_edge_cases_decodes() -> None:
    payload = _read_fixture("syntax_edge_cases.toon")
    out = deccan_toon.loads(payload)
    assert len(out) >= 5
    assert all("payload" in row for row in out)


def test_fixture_unicode_stress_decodes_utf8() -> None:
    payload = _read_fixture("global_text.toon")
    out = deccan_toon.loads(payload)
    assert len(out) >= 5
    # Ensure we preserved non-ascii content.
    texts = [row["text"] for row in out]
    assert any("🚀" in t for t in texts)
    assert any(any("\u0600" <= ch <= "\u06FF" for ch in t) for t in texts)  # Arabic


def test_fixture_type_chaos_invariants() -> None:
    payload = _read_fixture("typing_strictness.toon")
    out = deccan_toon.loads(payload)
    assert len(out) >= 5

    a_types = {type(row["A"]) for row in out}
    b_types = {type(row["B"]) for row in out}
    c_types = {type(row["C"]) for row in out}

    # Column A mixes ints and floats.
    assert int in a_types
    assert float in a_types
    # Column B mixes bool and None.
    assert bool in b_types
    assert type(None) in b_types
    # Column C is a JSON string (not a dict).
    assert c_types == {str}


def test_fixture_large_payload_decodes_row_count() -> None:
    payload = _read_fixture("large_payload.toon")
    out = deccan_toon.loads(payload)
    assert len(out) == 10_000
    # Spot-check required keys exist in every row.
    for row in (out[0], out[len(out) // 2], out[-1]):
        assert {"timestamp", "agent_id", "complexity_score", "memory_usage"} <= set(row)


