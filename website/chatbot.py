"""Compatibility entry point; prefer streamlit run website/Home.py."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "pages" / "1_💬_聊天室.py"), run_name="__main__")
