import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("src"))

import deccan_toon


@pytest.mark.smoke
def test_smoke_dumps_loads() -> None:
    data = [{"id": 1, "name": "Pune"}, {"id": 2, "name": "Mumbai"}]
    assert deccan_toon.loads(deccan_toon.dumps(data)) == data
