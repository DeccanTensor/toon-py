import sys, os

sys.path.insert(0, os.path.abspath("src"))
import deccan_toon

data = [{"id": 1, "name": "Pune"}, {"id": 2, "name": "Mumbai"}]
print(deccan_toon.dumps(data))
