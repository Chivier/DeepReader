"""Stable application paths and validation for user-supplied book names."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)
WEBSITE_DIR = PROJECT_ROOT / "website"
BOOK_PROMPT_DIR = WEBSITE_DIR / "book_prompt"
CHAT_HISTORY_DIR = WEBSITE_DIR / "chat_history"
BOOKMARKS_DIR = WEBSITE_DIR / "bookmarks"
DATA_DIR = Path(os.getenv("DEEPREADER_DATA_DIR", str(PROJECT_ROOT / "data" / "books"))).expanduser().resolve()

def validate_book_name(name):
    """Reject path components; preserve meaningful Chinese and Unicode names."""
    if not isinstance(name, str):
        raise ValueError("请输入书籍名称")
    name = name.strip()
    if not name or len(name) > 120:
        raise ValueError("书籍名称应为 1–120 个字符")
    if name in {".", ".."} or any(c in '<>:"/\\|?*' or ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError("书籍名称不能包含路径分隔符、控制字符或文件名保留字符")
    return name

def book_directory(name):
    name = validate_book_name(name)
    path = DATA_DIR / name
    if path.resolve().parent != DATA_DIR:
        raise ValueError("书籍目录必须位于数据目录内")
    return path
