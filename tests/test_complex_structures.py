import os
import sys
import time
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _complex_fixtures_dir() -> Path:
    return _repo_root() / "tests" / "testdata" / "complex"


def _read_complex_fixture(name: str) -> str:
    path = _complex_fixtures_dir() / name
    if not path.exists():
        pytest.fail(
            f"Missing complex fixture {name} at {path.as_posix()}. "
            "Generate/commit fixtures/complex/* before running tests."
        )
    return path.read_text(encoding="utf-8")


def _depth_of_nested_chain(node: dict[str, Any]) -> int:
    depth = 0
    cur = node
    while True:
        depth += 1
        assert cur.get("level") == depth
        child = cur.get("child")
        assert isinstance(child, list)
        if not child:
            return depth
        assert len(child) == 1
        assert isinstance(child[0], dict)
        cur = child[0]


@pytest.mark.integration
def test_recursion_limit() -> None:
    payload = _read_complex_fixture("nested_depth.toon")
    try:
        data = deccan_toon.loads(payload)
    except RecursionError as e:  # pragma: no cover
        pytest.fail(f"loads raised RecursionError: {e}")

    assert isinstance(data, list)
    assert len(data) == 1
    assert isinstance(data[0], dict)
    assert _depth_of_nested_chain(data[0]) == 50


@pytest.mark.integration
def test_polymorphic_rows() -> None:
    payload = _read_complex_fixture("mixed_schema_arrays.toon")
    data = deccan_toon.loads(payload)

    assert isinstance(data, list)
    assert len(data) == 3

    item1, item2, item3 = data

    # Item 1: {"id": 1, "tags": ["a", "b"]}
    assert item1["id"] == 1
    assert isinstance(item1["tags"], list)
    assert all(isinstance(x, str) for x in item1["tags"])

    # Item 2: {"id": 2, "meta": {"x": 10, "y": 20}}
    assert item2["id"] == 2
    assert isinstance(item2["meta"], dict)
    assert item2["meta"]["x"] == 10
    assert item2["meta"]["y"] == 20

    # Item 3: {"id": 3, "matrix": [[1, 2], [3, 4]]}
    assert item3["id"] == 3
    assert isinstance(item3["matrix"], list)
    assert all(isinstance(row, list) for row in item3["matrix"])
    assert item3["matrix"] == [[1, 2], [3, 4]]

    # Spec check: our current encoder uses union-of-keys and encodes missing fields as null,
    # so decoded rows will include the field with value None (not omitted).
    assert item1.get("meta") is None
    assert item1.get("matrix") is None
    assert item2.get("tags") is None
    assert item2.get("matrix") is None
    assert item3.get("tags") is None
    assert item3.get("meta") is None


@pytest.mark.integration
def test_large_file_integrity() -> None:
    payload = _read_complex_fixture("real_world_config.toon")

    original_data = deccan_toon.loads(payload)
    assert isinstance(original_data, list)
    assert len(original_data) == 1
    assert isinstance(original_data[0], dict)

    # Round-trip and re-load to ensure stability.
    restored_data = deccan_toon.loads(deccan_toon.dumps(original_data))
    assert original_data == restored_data


@pytest.mark.integration
@pytest.mark.benchmark
def test_benchmark_nested_depth_parse_under_500ms() -> None:
    payload = _read_complex_fixture("nested_depth.toon")

    # Warm-up to reduce one-time costs (imports/regex compilation) impacting the measurement.
    _ = deccan_toon.loads(payload)

    start = time.perf_counter()
    _ = deccan_toon.loads(payload)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert elapsed_ms <= 500.0, f"nested_depth.toon parse took {elapsed_ms:.2f}ms (>500ms)"
