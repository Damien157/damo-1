import sys
from pathlib import Path

# ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
# ensure both project root and src are importable
sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
