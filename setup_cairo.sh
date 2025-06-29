#!/bin/bash
# Set environment variable for Cairo library on macOS
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
echo "Cairo library path set. Now run: streamlit run website/chatbot.py"