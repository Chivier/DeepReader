"""
书籍管理页面
支持添加新书籍并自动爬取豆瓣数据
"""

import streamlit as st
import os
import sys
import threading
import time
from datetime import datetime

# 添加父目录到路径，以便导入 reader 模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from reader import douban_crawler, douban_cleaning, parse_review, report

# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    page_title="DeepReader - 书籍管理",
    page_icon="📚",
    layout="wide"
)

st.title("📚 书籍管理")

# ============================================================================
# 添加新书籍功能
# ============================================================================
st.header("➕ 添加新书籍")

with st.form("add_book_form"):
    book_name = st.text_input(
        "📖 书名", 
        placeholder="请输入要添加的书籍名称...",
        help="请输入准确的书名，系统将自动搜索豆瓣相关信息"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        douban_count = st.selectbox(
            "🔢 豆瓣爬取数量",
            options=[1, 2, 3, 5],
            index=0,
            help="选择要爬取的豆瓣版本数量（推荐选择1）"
        )
    
    with col2:
        auto_process = st.checkbox(
            "🤖 自动处理",
            value=True,
            help="是否自动完成所有处理步骤"
        )
    
    submit_button = st.form_submit_button("🚀 开始添加", use_container_width=True)

# ============================================================================
# 书籍处理逻辑
# ============================================================================
def show_waiting_animation(thread, progress_bar, status_text):
    """显示等待动画"""
    progress = 0
    while thread.is_alive():
        progress = (progress + 1) % 100
        progress_bar.progress(progress)
        time.sleep(0.1)
    progress_bar.progress(100)

def process_book_pipeline(book_name, douban_count, auto_process):
    """执行书籍处理管道"""
    
    # 创建状态显示区域
    status_container = st.container()
    
    with status_container:
        st.subheader(f"🔄 正在处理《{book_name}》")
        
        # 步骤1: 爬取豆瓣数据
        st.write("**步骤1: 爬取豆瓣书评数据**")
        progress_bar_1 = st.progress(0)
        status_text_1 = st.empty()
        
        try:
            status_text_1.text("正在搜索豆瓣图书信息...")
            douban_spider = douban_crawler.DoubanBookSpider()
            
            # 在线程中运行爬虫
            crawl_thread = threading.Thread(
                target=douban_spider.crawl_book, 
                args=(book_name, douban_count)
            )
            crawl_thread.start()
            
            # 显示进度动画
            show_waiting_animation(crawl_thread, progress_bar_1, status_text_1)
            
            status_text_1.text("✅ 豆瓣数据爬取完成")
            st.success("豆瓣书评数据爬取成功！")
            
        except Exception as e:
            st.error(f"豆瓣数据爬取失败: {e}")
            return False
        
        # 步骤2: 清理豆瓣数据
        st.write("**步骤2: 清理和处理豆瓣数据**")
        progress_bar_2 = st.progress(0)
        status_text_2 = st.empty()
        
        try:
            status_text_2.text("正在清理豆瓣数据...")
            
            clean_thread = threading.Thread(
                target=douban_cleaning.clean_all_douban_files,
                args=(f"{book_name}/website",)
            )
            clean_thread.start()
            
            show_waiting_animation(clean_thread, progress_bar_2, status_text_2)
            
            status_text_2.text("✅ 数据清理完成")
            st.success("豆瓣数据清理成功！")
            
        except Exception as e:
            st.error(f"数据清理失败: {e}")
            return False
        
        # 步骤3: 解析书评
        st.write("**步骤3: 解析和分类书评**")
        progress_bar_3 = st.progress(0)
        status_text_3 = st.empty()
        
        try:
            status_text_3.text("正在解析书评内容...")
            
            parse_thread = threading.Thread(
                target=parse_review.parse_reviews,
                args=(book_name,)
            )
            parse_thread.start()
            
            show_waiting_animation(parse_thread, progress_bar_3, status_text_3)
            
            status_text_3.text("✅ 书评解析完成")
            st.success("书评解析成功！")
            
        except Exception as e:
            st.error(f"书评解析失败: {e}")
            return False
        
        # 步骤4: 生成报告
        st.write("**步骤4: 生成综合报告**")
        progress_bar_4 = st.progress(0)
        status_text_4 = st.empty()
        
        try:
            status_text_4.text("正在生成综合报告...")
            
            report_thread = threading.Thread(
                target=report.report_parser,
                args=(book_name,)
            )
            report_thread.start()
            
            show_waiting_animation(report_thread, progress_bar_4, status_text_4)
            
            status_text_4.text("✅ 报告生成完成")
            st.success("综合报告生成成功！")
            
        except Exception as e:
            st.error(f"报告生成失败: {e}")
            return False
        
        # 步骤5: 创建书籍提示文件
        st.write("**步骤5: 创建书籍对话提示**")
        
        try:
            create_book_prompt(book_name)
            st.success("书籍提示文件创建成功！")
            
        except Exception as e:
            st.error(f"创建书籍提示失败: {e}")
            return False
        
        # 完成
        st.balloons()
        st.success(f"🎉 《{book_name}》 添加完成！现在可以在聊天界面中选择这本书进行对话了。")
        
        return True

def create_book_prompt(book_name):
    """创建书籍对话提示文件"""
    
    # 查找书籍报告文件
    report_path = f"{book_name}/final_report.md"
    if not os.path.exists(report_path):
        # 尝试其他可能的路径
        possible_paths = [
            f"{book_name}/report.md",
            f"{book_name}/summary.md",
            f"{book_name}/book_summary.txt"
        ]
        
        report_content = ""
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                break
        
        if not report_content:
            # 如果找不到报告，创建基础提示
            report_content = f"""
# 《{book_name}》

这是关于《{book_name}》的基础信息。系统已完成数据收集和处理，但未找到详细的报告文件。

## 基本信息
- 书名: {book_name}
- 数据来源: 豆瓣书评
- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 可讨论的话题
- 书籍的主要内容和情节
- 读者的评价和感受
- 书中的人物和主题
- 作品的文学价值和社会意义

请基于豆瓣书评数据和用户兴趣展开讨论。
"""
    else:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
    
    # 创建书籍提示目录
    prompt_dir = "website/book_prompt"
    os.makedirs(prompt_dir, exist_ok=True)
    
    # 写入书籍提示文件
    prompt_file = f"{prompt_dir}/{book_name}.md"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

# ============================================================================
# 执行书籍添加
# ============================================================================
if submit_button and book_name:
    if book_name.strip():
        # 检查书籍是否已存在
        prompt_dir = "website/book_prompt"
        existing_books = []
        if os.path.exists(prompt_dir):
            existing_books = [f[:-3] for f in os.listdir(prompt_dir) if f.endswith('.md')]
        
        if book_name in existing_books:
            st.warning(f"书籍《{book_name}》已存在，是否要重新处理？")
            if st.button("确认重新处理"):
                process_book_pipeline(book_name, douban_count, auto_process)
        else:
            process_book_pipeline(book_name, douban_count, auto_process)
    else:
        st.error("请输入有效的书名")

# ============================================================================
# 现有书籍管理
# ============================================================================
st.header("📖 现有书籍")

# 加载现有书籍列表
prompt_dir = "website/book_prompt"
if os.path.exists(prompt_dir):
    existing_books = [f[:-3] for f in os.listdir(prompt_dir) if f.endswith('.md')]
    
    if existing_books:
        st.write(f"当前共有 **{len(existing_books)}** 本书籍：")
        
        # 创建书籍网格显示
        cols = st.columns(3)
        for i, book in enumerate(existing_books):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"**📚 {book}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💬 对话", key=f"chat_{i}"):
                            st.query_params["book"] = book
                            st.switch_page("pages/1_💬_聊天室.py")
                    with col2:
                        if st.button("🗑️ 删除", key=f"delete_{i}"):
                            if st.session_state.get(f"confirm_delete_{i}"):
                                # 执行删除
                                try:
                                    os.remove(f"{prompt_dir}/{book}.md")
                                    st.success(f"已删除《{book}》")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"删除失败: {e}")
                            else:
                                st.session_state[f"confirm_delete_{i}"] = True
                                st.warning("再次点击确认删除")
    else:
        st.info("还没有添加任何书籍，请使用上方的表单添加新书籍。")
else:
    st.info("书籍目录不存在，请先添加一本书籍。")

# ============================================================================
# 使用说明
# ============================================================================
with st.expander("📋 使用说明"):
    st.markdown("""
    ## 🔧 功能说明
    
    ### 添加新书籍
    1. **输入书名**: 请输入准确的书籍名称
    2. **选择爬取数量**: 建议选择1，避免数据冗余
    3. **自动处理**: 勾选后将自动完成所有步骤
    4. **点击开始**: 系统将自动执行以下步骤：
       - 爬取豆瓣书评数据
       - 清理和结构化数据
       - 解析书评内容
       - 生成综合报告
       - 创建对话提示文件
    
    ### 管理现有书籍
    - **对话**: 跳转到聊天界面与该书进行对话
    - **删除**: 删除书籍和相关数据（需要二次确认）
    
    ## ⚠️ 注意事项
    - 请确保网络连接正常，爬取过程需要访问豆瓣
    - 处理时间取决于书评数量，通常需要几分钟
    - 建议一次只添加一本书，避免系统负载过重
    - 删除操作不可恢复，请谨慎操作
    
    ## 🛠️ 技术说明
    - 数据来源：豆瓣读书书评
    - 处理方式：AI 分析和分类
    - 存储格式：Markdown 文件
    - 支持格式：中英文书籍
    """)

# ============================================================================
# 侧边栏状态
# ============================================================================
with st.sidebar:
    st.markdown("### 📊 系统状态")
    
    # 显示书籍数量
    if os.path.exists(prompt_dir):
        book_count = len([f for f in os.listdir(prompt_dir) if f.endswith('.md')])
        st.metric("已添加书籍", book_count)
    else:
        st.metric("已添加书籍", 0)
    
    # 显示磁盘使用情况
    st.markdown("### 💾 存储信息")
    if os.path.exists("."):
        import shutil
        total, used, free = shutil.disk_usage(".")
        st.metric(
            "可用空间", 
            f"{free // (1024**3)} GB",
            help=f"总空间: {total // (1024**3)} GB"
        )
    
    st.markdown("### 🔗 快速导航")
    if st.button("💬 返回聊天", use_container_width=True):
        st.switch_page("chatbot.py")