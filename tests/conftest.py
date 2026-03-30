import sys
from pathlib import Path
import pytest

# add the project root directory to the Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC = ROOT_DIR / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# add path to man pages in the data/ folder to the Python path
DATA_DIR = ROOT_DIR / "src" / "data"

@pytest.fixture
def man_page_path():
    assert DATA_DIR.is_dir(), f"Data directory not found at {DATA_DIR}"
    return DATA_DIR