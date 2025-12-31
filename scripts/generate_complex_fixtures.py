"""
Generate complex TOON fixtures for parser stress-testing.

Outputs (relative to repo root):
  fixtures/complex/nested_depth.toon
  fixtures/complex/mixed_schema_arrays.toon
  fixtures/complex/real_world_config.toon

Usage:
  poetry run python scripts/generate_complex_fixtures.py
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _import_deccan_toon():
    # Allow running from a fresh repo checkout without installation.
    repo_root = _repo_root()
    sys.path.insert(0, str(repo_root / "src"))
    import deccan_toon  # type: ignore

    return deccan_toon


def _write_toon(path: Path, data: list[dict[str, Any]]) -> float:
    deccan_toon = _import_deccan_toon()
    payload = deccan_toon.dumps(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8", newline="\n")
    return path.stat().st_size / 1024.0


def _nested_depth_dataset(depth: int = 50) -> list[dict[str, Any]]:
    """
    Structure:
      [{"level": 1, "child": [{"level": 2, "child": [...]}]}]
    """

    def make_node(level: int) -> dict[str, Any]:
        if level >= depth:
            return {"level": level, "child": []}
        return {"level": level, "child": [make_node(level + 1)]}

    return [make_node(1)]


def _mixed_schema_arrays_dataset() -> list[dict[str, Any]]:
    return [
        {"id": 1, "tags": ["a", "b"]},
        {"id": 2, "meta": {"x": 10, "y": 20}},
        {"id": 3, "matrix": [[1, 2], [3, 4]]},
    ]


def _real_world_config_dataset() -> list[dict[str, Any]]:
    """
    A "real world"-style config inspired by package.json / extension-manifest
    patterns and Kubernetes-style deployment configs. Includes:
      - URLs
      - Semver ranges like "^1.2.0"
      - Punctuation-heavy description text

    Reference inspiration (public docs):
      - VS Code extension manifest fields (package.json): https://code.visualstudio.com/api/references/extension-manifest
      - Kubernetes Deployment concept: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
    """

    config: dict[str, Any] = {
        "name": "deccan-toon-stress-config",
        "version": "0.2.0",
        "description": "Stress config: URLs, semver, punctuation; nested objects.",
        "homepage": "https://github.com/DeccanTensor/toon-py",
        "repository": {"type": "git", "url": "https://github.com/DeccanTensor/toon-py.git"},
        "bugs": {"url": "https://github.com/DeccanTensor/toon-py/issues"},
        "engines": {"python": ">=3.10", "node": ">=18.0.0"},
        "dependencies": {
            "hypothesis": "^6.148.8",
            "pytest": "^9.0.2",
            "requests": "^2.32.0",
        },
        "contributes": {
            "commands": [
                {"command": "deccan.toon.encode", "title": "TOON: Encode (serialize)"},
                {"command": "deccan.toon.decode", "title": "TOON: Decode (parse)"},
            ],
            "configuration": {
                "title": "Deccan TOON",
                "properties": {
                    "toon.strict": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable strict parsing (recommended).",
                    },
                    "toon.maxDepth": {
                        "type": "number",
                        "default": 50,
                        "description": "Max nesting depth before rejecting.",
                    },
                    "toon.endpoints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "https://api.deccantensor.com/v1/toon/encode",
                            "https://api.deccantensor.com/v1/toon/decode",
                        ],
                    },
                },
            },
        },
        "deployment": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "toon-parser", "labels": {"app": "toon-parser"}},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "toon-parser"}},
                "template": {
                    "metadata": {"labels": {"app": "toon-parser"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "parser",
                                "image": "ghcr.io/deccantensor/toon-parser:0.2.0",
                                "ports": [{"containerPort": 8080}],
                                "env": [
                                    {"name": "TOON_STRICT", "value": "true"},
                                    {"name": "TOON_MAX_DEPTH", "value": "50"},
                                ],
                                "resources": {
                                    "limits": {"cpu": "500m", "memory": "512Mi"},
                                    "requests": {"cpu": "250m", "memory": "256Mi"},
                                },
                                "livenessProbe": {
                                    "httpGet": {"path": "/healthz", "port": 8080},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10,
                                },
                            }
                        ]
                    },
                },
            },
        },
        "notes": [
            "This config contains deep nesting, lists-of-objects, and mixed types.",
            "It should remain valid JSON when re-serialized.",
            "Semver examples: '^1.2.0', '~2.3.4', '>=3.10'.",
        ],
    }

    # Add some extra (but deterministic) noise to increase entropy and nesting.
    random_sections = []
    for i in range(25):
        random_sections.append(
            {
                "id": i,
                "enabled": bool(i % 2),
                "thresholds": [round(random.random(), 6) for _ in range(10)],
                "routes": [
                    {"path": f"/v{i}/items", "method": "GET"},
                    {"path": f"/v{i}/items", "method": "POST"},
                ],
                "metadata": {
                    "owner": "qa-architect@deccantensor.com",
                    "ticket": f"QA-{1000 + i}",
                    "doc": f"https://docs.deccantensor.com/specs/toon/{i}",
                },
            }
        )
    config["stress"] = {"sections": random_sections}

    # Ensure the "real world" structure is JSON-serializable.
    json.dumps(config, ensure_ascii=False)

    return [
        {
            "id": 1,
            "source": "real-world-config (embedded)",
            "config": config,
        }
    ]


def main() -> int:
    # Deterministic output unless overridden.
    seed = os.getenv("TOON_COMPLEX_FIXTURE_SEED", "1337")
    random.seed(seed)

    root = _repo_root()
    out_dir = root / "tests" / "testdata" / "complex"

    outputs = [
        (out_dir / "nested_depth.toon", _nested_depth_dataset()),
        (out_dir / "mixed_schema_arrays.toon", _mixed_schema_arrays_dataset()),
        (out_dir / "real_world_config.toon", _real_world_config_dataset()),
    ]

    for path, data in outputs:
        size_kb = _write_toon(path, data)
        print(f"Wrote {path.as_posix()} ({size_kb:.2f} KB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


