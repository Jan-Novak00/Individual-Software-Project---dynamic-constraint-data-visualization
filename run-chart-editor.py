import runpy
import sys
from pathlib import Path

main_dir = Path(__file__).parent / "editable-plots"
sys.path.insert(0, str(main_dir))

runpy.run_path(str(main_dir / "main.py"), run_name="__main__")