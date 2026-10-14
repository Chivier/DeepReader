#!/bin/bash

set -euo pipefail
website_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(dirname -- "$website_dir")"
cd "$project_dir"

echo "🚀 启动 DeepReader..."

# 设置环境变量（如果需要）
if [[ "$(uname)" == "Darwin" ]]; then
    export DYLD_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_LIBRARY_PATH:-}"
fi

# 启动 Streamlit 应用
exec python -m streamlit run "$website_dir/Home.py" "$@"

# 备选命令（如果需要指定端口）
# streamlit run Home.py --server.port 8501
