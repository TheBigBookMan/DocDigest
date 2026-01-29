import sys
from pathlib import Path

app_dir = Path(__file__).parent.parent / 'app'
sys.path.insert(0, str(app_dir))