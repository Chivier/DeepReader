"""
Utility functions for DeepReader web interface
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if not"""
    os.makedirs(path, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def generate_file_hash(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def save_json_data(data: Dict, filepath: str) -> bool:
    """Save data as JSON with error handling"""
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {e}")
        return False


def load_json_data(filepath: str) -> Optional[Dict]:
    """Load JSON data with error handling"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None


def format_timestamp(timestamp: float = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def validate_book_name(book_name: str) -> bool:
    """Validate book name input"""
    if not book_name or not book_name.strip():
        return False
    if len(book_name.strip()) < 2:
        return False
    return True


def get_available_books(book_prompt_dir: str) -> List[str]:
    """Get list of available books"""
    if not os.path.exists(book_prompt_dir):
        return []
    
    books = []
    for file in os.listdir(book_prompt_dir):
        if file.endswith('.md'):
            books.append(file[:-3])  # Remove .md extension
    
    return sorted(books)


def calculate_reading_time(text: str, wpm: int = 250) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    return max(1, round(word_count / wpm))


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def create_download_link(content: str, filename: str, label: str) -> str:
    """Create download link for content"""
    import base64
    
    b64_content = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64_content}" download="{filename}">{label}</a>'
    return href


class SessionManager:
    """Manage Streamlit session state"""
    
    @staticmethod
    def init_session_var(key: str, default_value) -> None:
        """Initialize session variable if not exists"""
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    @staticmethod
    def clear_session_vars(keys: List[str]) -> None:
        """Clear specified session variables"""
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def get_session_var(key: str, default=None):
        """Get session variable with default"""
        return st.session_state.get(key, default)


class ProgressTracker:
    """Track progress for long-running operations"""
    
    def __init__(self, total_steps: int, description: str = "Processing..."):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
    def update(self, step_description: str = None):
        """Update progress by one step"""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        self.progress_bar.progress(progress)
        
        if step_description:
            self.status_text.text(f"{self.description}: {step_description}")
        else:
            self.status_text.text(f"{self.description}: {self.current_step}/{self.total_steps}")
    
    def complete(self, completion_message: str = "Completed!"):
        """Mark progress as complete"""
        self.progress_bar.progress(1.0)
        self.status_text.text(completion_message)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_file_info(filepath: str) -> Dict:
    """Get file information"""
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': format_timestamp(stat.st_mtime),
        'created': format_timestamp(stat.st_ctime)
    }