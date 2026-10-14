"""Shared runtime configuration for every Streamlit entry point."""
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
def configure_import_paths():
    for directory in (project_root, str(Path(__file__).resolve().parent)):
        if directory not in sys.path:
            sys.path.insert(0, directory)

configure_import_paths()

from reader.paths import (  # noqa: E402
    BOOKMARKS_DIR,
    BOOK_PROMPT_DIR,
    CHAT_HISTORY_DIR,
    book_directory,
    validate_book_name,
)
