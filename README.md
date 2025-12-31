<div align="left">
  <h1>Deccan Toon</h1>

  <a href="https://pypi.org/project/deccan-toon/">
    <img src="https://img.shields.io/pypi/v/deccan-toon?color=orange&label=pypi%20package" alt="PyPI version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/deccan-toon" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/spec-TOON%20v3.0-blue" alt="Spec v3.0">
  <img src="https://img.shields.io/github/license/DeccanTensor/toon-py" alt="License">
</div>

<br>

> **"First, we shape our tools, thereafter they shape us."**

**Deccan Toon** is a strict, high-velocity implementation of the [TOON v3.0 Specification](https://github.com/toon-format/toon).

While other parsers focus on flexibility, **Deccan Toon** focuses on **correctness, security, and type fidelity**. We built this to be the "Newtonsoft" of the TOON ecosystem—robust enough for enterprise agents and critical infrastructure.

---

### 📉 Token Economics (The "Why")

Standard JSON repeats keys for every single row (`id`, `name`, `status`), wasting precious context window space in LLMs (GPT-4, Claude). **TOON** sends the header once.

**Payload Size Comparison (1000 items):**
```text
████████████████████ 100% - JSON (Standard)
████████████         60%  - CSV (No types)
███████████          55%  - TOON (Typed & Clean)
```

Stop paying for repeated keys. Save context window space for actual intelligence.

---

### 📦 Installation

```bash
pip install deccan-toon
```

---
### ⚡ Quick Start
```python
import deccan_toon

# 1. Define your data (List of Dicts)
data = [
    {"id": 1, "agent": "Alpha", "status": "Active", "score": 0.98},
    {"id": 2, "agent": "Beta",  "status": "Idle",   "score": None},
    {"id": 3, "agent": "Gamma", "status": "Sleep",  "score": 0.45}
]

# 2. Serialize (Python -> TOON)
payload = deccan_toon.dumps(data)

print(payload)
# Output:
# items[3]{id,agent,status,score}:
#   1, Alpha, Active, 0.98
#   2, Beta, Idle, null
#   3, Gamma, Sleep, 0.45

# 3. Deserialize (TOON -> Python)
restored = deccan_toon.loads(payload)
```

---

### 🛡️ The Deccan Difference

- **Strict Compliance**: Fully compliant with TOON v3.0 (Handling nesting, typed arrays, and sparse data).

- **Security First**: Includes protections against "Billion Laughs" expansion attacks and deep recursion.

- **Type Safety**: Unlike CSV, we preserve int, float, bool, and null types with 100% fidelity.

- **Zero Dependencies**: Runs on pure Python standard library.
