![PyPI](https://img.shields.io/pypi/v/deccan-toon) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/pypi/l/deccan-toon) ![Build Status](https://github.com/DeccanTensor/toon-py/actions/workflows/publish.yml/badge.svg)

# Deccan Toon

Battling JSON bloat with Pythonic elegance. A high-efficiency TOON serializer.

## 📉 Token Economics (Why Use This?)

JSON wastes tokens by repeating keys.

```text
Payload Size Comparison (1000 items):
████████████████████ 100% - JSON (Standard)
████████████         60%  - CSV
███████████          55%  - TOON (Cleaner & Typer-Safe)
```

Stop paying for repeated keys. Save context window space for actual intelligence.

## Installation

```bash
pip install deccan-toon
```

## Usage

```python
import deccan_toon

data = [{"id": 1, "name": "Pune"}, {"id": 2, "name": "Mumbai"}]
print(deccan_toon.dumps(data))
```
