"""
DeepReader 主页
提供导航到各个功能页面
"""

import streamlit as st

# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    page_title="DeepReader - AI深度阅读助手",
    page_icon="📚",
    layout="wide"
)

# ============================================================================
# 主页内容
# ============================================================================
st.title("📚 DeepReader - AI深度阅读助手")
st.markdown("让AI帮助你更深入地理解每一本书")

st.markdown("---")

# 功能介绍
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💬 深度对话")
    st.markdown("""
    与AI进行深入的书籍讨论：
    - 📖 选择已有书籍开始对话
    - 💭 探讨书中的核心思想
    - 🎯 获得个性化的阅读见解
    - 🔖 生成精美的阅读书签
    
    [开始聊天 →](聊天室)
    """)

with col2:
    st.markdown("### ➕ 添加新书")
    st.markdown("""
    为新书籍创建AI对话模板：
    - 🔍 自动爬取豆瓣书评
    - 📹 搜索相关视频解读
    - 📝 生成高质量阅读指南
    - ✨ 一键添加到书籍库
    
    [添加新书 →](添加新书)
    """)

st.markdown("---")

# 使用说明
st.markdown("### 🚀 快速开始")
st.markdown("""
1. **新用户**：先访问"添加新书"添加你想读的书
2. **老用户**：直接进入"聊天室"选择书籍开始对话
3. **探索更多**：尝试不同的问题角度，获得更丰富的见解
""")

# 侧边栏
with st.sidebar:
    st.markdown("### 🌟 关于 DeepReader")
    st.markdown("""
    DeepReader 是一个AI驱动的深度阅读助手，通过：
    - 智能分析海量书评
    - 多维度理解书籍内容
    - 生成个性化阅读体验
    
    帮助你更好地理解和欣赏每一本书。
    """)
    
    st.markdown("### 🛠️ 功能特色")
    st.markdown("""
    - **智能对话**：像朋友一样自然交流
    - **深度分析**：挖掘书籍深层含义
    - **视觉书签**：保存精彩阅读瞬间
    - **持续学习**：不断丰富书籍库
    """)
    
    st.markdown("### 📊 系统状态")
    import os
    book_prompt_dir = os.path.join(os.path.dirname(__file__), "book_prompt")
    if os.path.exists(book_prompt_dir):
        book_count = len([f for f in os.listdir(book_prompt_dir) if f.endswith('.md')])
        st.metric("书籍总数", book_count)
    else:
        st.metric("书籍总数", 0)