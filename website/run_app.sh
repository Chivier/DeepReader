#!/bin/bash

# DeepReader Streamlit 多页面应用启动脚本

echo "🚀 启动 DeepReader..."

# 设置环境变量（如果需要）
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# 启动 Streamlit 应用
streamlit run Home.py

# 备选命令（如果需要指定端口）
# streamlit run Home.py --server.port 8501