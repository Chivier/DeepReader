"""Compatibility entry point for the maintained add-book page."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "pages" / "2_➕_添加新书.py"), run_name="__main__")
