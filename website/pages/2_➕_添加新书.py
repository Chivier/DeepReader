"""
书评爬取与Prompt生成页面
支持豆瓣书评爬取、视频书评搜索和高质量prompt生成
"""

import streamlit as st
import os
import sys
import threading
import time
import json
from datetime import datetime
import subprocess
import queue

# 添加reader目录到系统路径
reader_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reader')
if reader_path not in sys.path:
    sys.path.append(reader_path)

import douban_crawler
import douban_cleaning
import video_cleaning
from parse_review import parse_reviews
import report
from bilibili_auto_crawler import auto_process_book_videos
import bilibili_auto_crawler

# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    page_title="DeepReader - 添加新书",
    page_icon="➕",
    layout="wide"
)

st.title("➕ 添加新书")
st.markdown("自动爬取书评并生成高质量的阅读prompt")

# ============================================================================
# 状态管理
# ============================================================================
if "generation_status" not in st.session_state:
    st.session_state.generation_status = {
        "current_step": "",
        "progress": 0,
        "logs": [],
        "is_running": False,
        "success": False,
        "error": None,
        "waiting_confirmation": False,
        "confirmation_type": None,
        "book_urls": [],
        "selected_book_url": None,
        "book_info": None
    }

if "status_queue" not in st.session_state:
    st.session_state.status_queue = queue.Queue()

# ============================================================================
# 辅助函数
# ============================================================================
def search_book_on_douban(book_name):
    """搜索豆瓣书籍并返回结果"""
    spider = douban_crawler.DoubanBookSpider()
    book_urls = spider.search_book(book_name)
    
    if book_urls:
        # 获取前3本书的信息
        books_info = []
        for i, url in enumerate(book_urls[:3]):
            info = spider.get_book_info(url)
            if info:
                info['url'] = url
                books_info.append(info)
        return books_info
    return []

def generate_book_prompt_sync(book_name, include_video, status_queue, selected_book_url=None, auto_mode=False):
    """同步生成书籍的完整处理流程（在线程中运行）"""
    def update_status(step, progress, log_message):
        """更新生成状态（线程安全）"""
        status_queue.put({
            "type": "update",
            "step": step,
            "progress": progress,
            "log": f"[{datetime.now().strftime('%H:%M:%S')}] {log_message}"
        })
    
    def run_with_progress(func, args, step_name, progress_start, progress_end):
        """带进度更新的函数运行"""
        update_status(step_name, progress_start, f"开始{step_name}...")
        
        try:
            result = func(*args)
            update_status(step_name, progress_end, f"✅ {step_name}完成")
            return result
        except Exception as e:
            update_status(step_name, progress_end, f"❌ {step_name}失败: {str(e)}")
            raise e
    
    try:
        # 1. 搜索豆瓣书籍
        if not selected_book_url:
            update_status("搜索书籍", 0, f"正在豆瓣搜索《{book_name}》...")
            books_info = search_book_on_douban(book_name)
            
            if not books_info:
                raise Exception("未在豆瓣找到相关书籍")
            
            if auto_mode:
                # 自动模式：选择第一本书
                selected_book_url = books_info[0]['url']
                update_status("自动选择", 5, f"自动选择：{books_info[0]['title']}")
            else:
                # 请求用户确认
                status_queue.put({
                    "type": "need_confirmation",
                    "confirmation_type": "book_selection",
                    "books_info": books_info
                })
                return  # 暂停执行，等待用户确认
        
        # 2. 爬取豆瓣书评（使用用户选择的URL）
        update_status("爬取豆瓣", 10, f"开始爬取《{book_name}》的豆瓣书评...")
        
        # 创建一个临时的爬虫函数来使用指定的URL
        def crawl_specific_book():
            spider = douban_crawler.DoubanBookSpider()
            # 获取书籍信息
            update_status("爬取豆瓣", 10, f"正在获取书籍信息...")
            book_info = spider.get_book_info(selected_book_url)
            
            # 创建保存目录
            save_dir = f"{book_name}/website"
            os.makedirs(save_dir, exist_ok=True)
            
            # 保存书籍信息
            with open(f"{save_dir}/book_info.json", 'w', encoding='utf-8') as f:
                json.dump(book_info, f, ensure_ascii=False, indent=2)
            
            # 获取评论URLs
            update_status("爬取豆瓣", 12, f"正在获取书评列表...")
            review_urls = spider.get_review_urls(selected_book_url, range=5)
            total_reviews = len(review_urls[:5])
            
            # 逐条获取评论内容
            reviews = []
            for i, review_url in enumerate(review_urls[:5]):
                update_status("爬取豆瓣", 12 + (i+1) * 8 / total_reviews, 
                            f"正在处理第 {i+1}/{total_reviews} 条书评")
                # 获取单条评论
                review_data = spider.get_reviews([review_url])
                if review_data:
                    reviews.extend(review_data)
                    # 保存评论
                    review_content = review_data[0][1]
                    with open(f"{save_dir}/review_{i+1}.txt", 'w', encoding='utf-8') as f:
                        f.write(review_content)
                time.sleep(2)  # 避免请求过快
        
        run_with_progress(
            crawl_specific_book,
            (),
            "爬取豆瓣书评",
            10, 20
        )
        
        # 3. 清理豆瓣数据
        run_with_progress(
            douban_cleaning.clean_all_douban_files,
            (f"{book_name}/website",),
            "清理豆瓣数据",
            20, 30
        )
        
        # 4. 自动搜索和处理视频
        if include_video:
            def video_process():
                update_status("搜索视频", 30, "正在搜索B站相关视频...")
                
                # 创建爬虫实例
                crawler = bilibili_auto_crawler.BilibiliAutoCrawler()
                
                # 搜索视频
                videos = crawler.search_videos(book_name)
                if not videos:
                    update_status("搜索视频", 35, "未找到相关视频")
                    return
                
                update_status("搜索视频", 35, f"找到 {len(videos)} 个相关视频")
                
                # 创建链接文件
                links_file = crawler.create_video_links_file(videos, book_name)
                
                # 下载视频（最多3个）
                max_videos = min(3, len(videos))
                for i, video in enumerate(videos[:max_videos]):
                    progress = 35 + (i + 1) * 15 / max_videos
                    video_title = video.get('title', '未知标题')[:30] + '...'
                    video_url = f"https://www.bilibili.com/video/{video.get('bvid', '')}"
                    update_status("下载视频", progress, 
                                f"正在处理第 {i+1}/{max_videos} 个视频：{video_title}\n链接：{video_url}")
                    
                    # 下载单个视频
                    try:
                        # 首先尝试使用 lux
                        video_dir = f"{book_name}/video"
                        os.makedirs(video_dir, exist_ok=True)
                        
                        # 尝试使用 lux 下载
                        lux_cmd = f"lux -o {video_dir} {video_url}"
                        lux_result = subprocess.run(lux_cmd, shell=True, capture_output=True, text=True)
                        
                        if lux_result.returncode == 0:
                            update_status("下载视频", progress, 
                                        f"✅ 使用 lux 成功下载视频 {i+1}")
                        else:
                            # lux 失败，尝试使用 yt-dlp
                            update_status("下载视频", progress, 
                                        f"lux 下载失败，尝试使用 yt-dlp...")
                            crawler.download_videos([video], book_name, 1)
                        
                        time.sleep(2)  # 避免请求过快
                    except Exception as e:
                        update_status("下载视频", progress, 
                                    f"视频 {i+1} 下载失败，跳过：{str(e)[:50]}...")
                        continue
                
                # 提取字幕
                update_status("提取字幕", 48, "正在提取视频字幕...")
                subtitle_text = crawler.extract_subtitles_text(book_name)
                
                update_status("视频处理完成", 50, f"✅ 视频处理完成，共处理 {max_videos} 个视频")
            
            run_with_progress(
                video_process,
                (),
                "搜索视频书评",
                30, 50
            )
            
            # 5. 清理视频数据
            def clean_video_data():
                try:
                    video_cleaning.clean_all_video_files(f"{book_name}/video")
                except Exception as e:
                    update_status("清理视频数据", 60, f"⚠️ 视频数据清理跳过: {str(e)}")
                    # 不抛出异常，继续执行
            
            run_with_progress(
                clean_video_data,
                (),
                "清理视频数据",
                50, 60
            )
        else:
            update_status("跳过视频处理", 60, "用户选择不包含视频书评")
        
        # 6. 解析书评
        def parse_reviews_with_status():
            try:
                update_status("解析书评", 60, "正在读取收集到的书评...")
                
                # 统计文件数量
                website_dir = f"{book_name}/website"
                video_dir = f"{book_name}/video"
                
                website_files = []
                video_files = []
                
                if os.path.exists(website_dir):
                    website_files = [f for f in os.listdir(website_dir) if f.endswith('.txt')]
                if os.path.exists(video_dir):
                    video_files = [f for f in os.listdir(video_dir) if f.endswith('.txt')]
                
                total_files = len(website_files) + len(video_files)
                update_status("解析书评", 65, f"找到 {len(website_files)} 个豆瓣书评，{len(video_files)} 个视频转录文本")
                
                # 执行解析
                update_status("解析书评", 70, "正在分析书评内容，提取关键信息...")
                parse_reviews(book_name)
                
                update_status("解析书评", 80, f"✅ 书评解析完成，共处理 {total_files} 个文件")
            except Exception as e:
                update_status("解析书评", 80, f"⚠️ 书评解析部分失败: {str(e)[:100]}...")
                # 不抛出异常，继续执行
        
        run_with_progress(
            parse_reviews_with_status,
            (),
            "解析书评内容",
            60, 80
        )
        
        # 7. 生成报告
        def generate_report_with_status():
            try:
                update_status("生成报告", 80, "正在整合所有分析结果...")
                
                # 检查是否有解析的数据
                parsed_data_path = f"{book_name}/parsed_data.json"
                if not os.path.exists(parsed_data_path):
                    # 如果没有解析数据，创建一个简单的报告
                    update_status("生成报告", 85, "未找到解析数据，生成基础报告...")
                    
                    # 读取原始书评创建简单报告
                    reviews = []
                    website_dir = f"{book_name}/website"
                    if os.path.exists(website_dir):
                        for file in os.listdir(website_dir):
                            if file.endswith('.txt') and not file.endswith('_cleaned.txt'):
                                with open(os.path.join(website_dir, file), 'r', encoding='utf-8') as f:
                                    reviews.append(f.read()[:500])  # 取前500字符
                    
                    # 创建简单报告
                    simple_report = f"""# 《{book_name}》书评汇总

## 收集到的书评摘要

"""
                    for i, review in enumerate(reviews[:5]):  # 最多显示5条
                        simple_report += f"### 书评 {i+1}\n{review}...\n\n"
                    
                    # 保存报告
                    report_path = f"{book_name}/report.md"
                    with open(report_path, "w", encoding="utf-8") as f:
                        f.write(simple_report)
                else:
                    # 执行正常的报告生成
                    report.report_parser(book_name)
                
                update_status("生成报告", 90, "✅ 综合报告生成完成")
            except Exception as e:
                update_status("生成报告", 90, f"⚠️ 报告生成部分失败: {str(e)[:100]}...")
                # 创建最基础的报告
                basic_report = f"""# 《{book_name}》阅读指南

## 书籍信息
书名：《{book_name}》

## 内容简介
（根据收集的书评整理）

本书的详细内容正在整理中...
"""
                report_path = f"{book_name}/report.md"
                os.makedirs(book_name, exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(basic_report)
        
        run_with_progress(
            generate_report_with_status,
            (),
            "生成综合报告",
            80, 90
        )
        
        # 8. 生成并保存prompt
        update_status("生成Prompt", 90, "正在生成最终的书籍prompt...")
        
        # 清理视频文件以节省空间（保留字幕）
        try:
            video_dir = f"{book_name}/video"
            if os.path.exists(video_dir):
                for file in os.listdir(video_dir):
                    file_path = os.path.join(video_dir, file)
                    # 只删除视频文件，保留txt字幕文件
                    if os.path.isfile(file_path) and not file.endswith('.txt'):
                        os.remove(file_path)
                        print(f"Removed video file: {file}")
        except Exception as e:
            print(f"Error cleaning video files: {e}")
        
        # 读取生成的报告
        report_path = f"{book_name}/report.md"
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            
            # 生成prompt格式
            prompt_content = f"""# 《{book_name}》深度阅读指南

## 书籍概览
{report_content}

## 讨论要点
- 探讨书中的核心主题和思想
- 分析主要人物的成长和变化
- 思考书中观点对现实生活的启发
- 分享个人的阅读感受和思考

## 推荐问题
1. 这本书最打动你的地方是什么？
2. 书中的哪个观点让你产生了新的思考？
3. 如果你是书中的主人公，你会做出什么不同的选择？
"""
            
            if auto_mode:
                # 自动模式：直接保存
                book_prompt_dir = os.path.join(os.path.dirname(__file__), "..", "book_prompt")
                os.makedirs(book_prompt_dir, exist_ok=True)
                
                prompt_file = os.path.join(book_prompt_dir, f"{book_name}.md")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(prompt_content)
                
                update_status("完成", 100, f"✅ 《{book_name}》的prompt已生成并保存")
                status_queue.put({"type": "success", "book_name": book_name})
            else:
                # 暂时保存prompt内容，等待用户确认
                status_queue.put({
                    "type": "need_confirmation",
                    "confirmation_type": "add_to_chat",
                    "prompt_content": prompt_content,
                    "book_name": book_name
                })
                
                update_status("完成", 100, f"✅ 《{book_name}》的prompt已生成，等待确认")
        else:
            raise Exception("报告生成失败，未找到报告文件")
            
    except Exception as e:
        # 失败时不删除已收集的数据
        update_status("错误", 100, f"❌ 生成失败: {str(e)}")
        update_status("提示", 100, "⚠️ 已收集的数据保留在相应目录中")
        status_queue.put({"type": "error", "error": str(e)})

# ============================================================================
# 主界面
# ============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📚 输入书籍信息")
    
    # 书名输入
    book_name = st.text_input(
        "书籍名称",
        placeholder="请输入要生成的书籍名称，如：人类简史",
        help="输入准确的书名有助于获得更好的搜索结果",
        disabled=st.session_state.generation_status["is_running"]
    )
    
    # 选项
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        include_video = st.checkbox(
            "包含视频书评",
            value=True,
            help="自动搜索B站等平台的视频书评",
            disabled=st.session_state.generation_status["is_running"]
        )
    
    with col_opt2:
        auto_mode = st.checkbox(
            "自动模式",
            value=True,
            help="跳过所有确认步骤，自动完成全流程",
            disabled=st.session_state.generation_status["is_running"]
        )
    
    # 生成按钮
    if st.button("🚀 开始生成", disabled=st.session_state.generation_status["is_running"]):
        if book_name:
            # 重置状态
            st.session_state.generation_status = {
                "current_step": "准备中",
                "progress": 0,
                "logs": [],
                "is_running": True,
                "success": False,
                "error": None,
                "waiting_confirmation": False,
                "confirmation_type": None,
                "book_urls": [],
                "selected_book_url": None,
                "book_info": None
            }
            st.session_state.status_queue = queue.Queue()
            
            # 在新线程中运行生成过程
            generation_thread = threading.Thread(
                target=generate_book_prompt_sync,
                args=(book_name, include_video, st.session_state.status_queue, None, auto_mode)
            )
            generation_thread.daemon = True
            generation_thread.start()
            st.rerun()
        else:
            st.error("请输入书籍名称")

with col2:
    st.markdown("### 📊 生成进度")
    
    # 当前步骤
    if st.session_state.generation_status["current_step"]:
        st.info(f"当前步骤: {st.session_state.generation_status['current_step']}")
    
    # 进度条
    progress = st.session_state.generation_status["progress"]
    st.progress(progress / 100)
    st.caption(f"进度: {progress}%")

# ============================================================================
# 确认界面
# ============================================================================
if st.session_state.generation_status["waiting_confirmation"]:
    st.markdown("---")
    
    # 书籍选择确认
    if st.session_state.generation_status["confirmation_type"] == "book_selection":
        st.markdown("### 📚 请确认书籍")
        st.markdown("找到以下相关书籍，请选择您要处理的书籍：")
        
        books_info = st.session_state.generation_status.get("books_info", [])
        for i, book in enumerate(books_info):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.write(f"**{book['title']}**")
            with col2:
                st.write(f"作者: {book['author']}")
            with col3:
                st.write(f"评分: {book['rating']}")
            with col4:
                if st.button(f"选择", key=f"select_book_{i}"):
                    # 继续处理选中的书籍
                    st.session_state.generation_status["selected_book_url"] = book['url']
                    st.session_state.generation_status["book_info"] = book
                    st.session_state.generation_status["waiting_confirmation"] = False
                    
                    # 重启线程继续处理
                    generation_thread = threading.Thread(
                        target=generate_book_prompt_sync,
                        args=(
                            book_name, 
                            include_video, 
                            st.session_state.status_queue,
                            book['url'],
                            False  # 用户手动确认后，不再使用自动模式
                        )
                    )
                    generation_thread.daemon = True
                    generation_thread.start()
                    st.rerun()
        
        # 查看豆瓣链接
        if books_info:
            st.markdown("---")
            st.markdown("**豆瓣链接：**")
            for book in books_info:
                st.markdown(f"- [{book['title']}]({book['url']})")
    
    # 添加到聊天确认
    elif st.session_state.generation_status["confirmation_type"] == "add_to_chat":
        st.markdown("### ✅ 生成完成")
        st.success(f"《{st.session_state.generation_status.get('book_name', '')}》的阅读指南已生成！")
        
        # 显示生成的内容预览
        with st.expander("查看生成的内容"):
            st.markdown(st.session_state.generation_status.get("prompt_content", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 确认添加到聊天室", type="primary"):
                # 保存prompt文件
                book_prompt_dir = os.path.join(os.path.dirname(__file__), "..", "book_prompt")
                os.makedirs(book_prompt_dir, exist_ok=True)
                
                book_name = st.session_state.generation_status.get("book_name", "")
                prompt_file = os.path.join(book_prompt_dir, f"{book_name}.md")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(st.session_state.generation_status.get("prompt_content", ""))
                
                # 重置状态
                st.session_state.generation_status = {
                    "current_step": "",
                    "progress": 0,
                    "logs": [],
                    "is_running": False,
                    "success": True,
                    "error": None,
                    "waiting_confirmation": False,
                    "confirmation_type": None,
                    "book_urls": [],
                    "selected_book_url": None,
                    "book_info": None,
                    "book_name": book_name
                }
                st.rerun()
        
        with col2:
            if st.button("❌ 取消"):
                # 重置状态
                st.session_state.generation_status = {
                    "current_step": "",
                    "progress": 0,
                    "logs": [],
                    "is_running": False,
                    "success": False,
                    "error": None,
                    "waiting_confirmation": False,
                    "confirmation_type": None,
                    "book_urls": [],
                    "selected_book_url": None,
                    "book_info": None
                }
                st.rerun()

# ============================================================================
# 处理队列中的状态更新
# ============================================================================
if st.session_state.generation_status["is_running"]:
    # 处理所有待处理的状态更新
    while not st.session_state.status_queue.empty():
        try:
            update = st.session_state.status_queue.get_nowait()
            
            if update["type"] == "update":
                st.session_state.generation_status["current_step"] = update["step"]
                st.session_state.generation_status["progress"] = update["progress"]
                st.session_state.generation_status["logs"].append(update["log"])
            elif update["type"] == "need_confirmation":
                st.session_state.generation_status["waiting_confirmation"] = True
                st.session_state.generation_status["confirmation_type"] = update["confirmation_type"]
                if update["confirmation_type"] == "book_selection":
                    st.session_state.generation_status["books_info"] = update["books_info"]
                elif update["confirmation_type"] == "add_to_chat":
                    st.session_state.generation_status["prompt_content"] = update["prompt_content"]
                    st.session_state.generation_status["book_name"] = update["book_name"]
            elif update["type"] == "success":
                st.session_state.generation_status["is_running"] = False
                st.session_state.generation_status["success"] = True
                st.session_state.generation_status["book_name"] = update["book_name"]
            elif update["type"] == "error":
                st.session_state.generation_status["is_running"] = False
                st.session_state.generation_status["error"] = update["error"]
        except queue.Empty:
            break
    
    # 自动刷新
    if not st.session_state.generation_status["waiting_confirmation"]:
        time.sleep(0.5)
        st.rerun()

# ============================================================================
# 日志显示
# ============================================================================
st.markdown("### 📝 处理日志")

# 显示日志
log_container = st.container()
with log_container:
    logs = st.session_state.generation_status["logs"]
    if logs:
        # 创建一个可滚动的容器
        with st.expander("查看详细日志", expanded=True):
            # 只显示最近的日志
            for log in logs[-15:]:
                # 如果日志包含换行，特殊处理
                if '\n' in log:
                    parts = log.split('\n', 1)
                    st.text(parts[0])
                    if len(parts) > 1:
                        st.caption(parts[1])
                else:
                    st.text(log)
    else:
        st.text("等待开始...")

# ============================================================================
# 成功提示
# ============================================================================
if st.session_state.generation_status["success"]:
    book_name = st.session_state.generation_status.get("book_name", "")
    st.success(f"🎉 《{book_name}》已成功添加到聊天室！")
    
    # 提供跳转按钮
    if st.button("📖 前往聊天页面"):
        # 设置 URL 参数
        st.query_params["book"] = book_name
        # 重置状态
        st.session_state.generation_status = {
            "current_step": "",
            "progress": 0,
            "logs": [],
            "is_running": False,
            "success": False,
            "error": None,
            "waiting_confirmation": False,
            "confirmation_type": None,
            "book_urls": [],
            "selected_book_url": None,
            "book_info": None
        }
        st.switch_page("pages/1_💬_聊天室.py")

# 错误提示
if st.session_state.generation_status.get("error"):
    st.error(f"生成失败: {st.session_state.generation_status['error']}")

# ============================================================================
# 侧边栏说明
# ============================================================================
with st.sidebar:
    st.markdown("### ➕ 使用说明")
    st.markdown("""
    1. **输入书名**: 输入想要生成prompt的书籍名称
    2. **选择选项**: 
       - 是否包含视频书评
       - 是否使用自动模式
    3. **开始生成**: 点击按钮开始自动处理
    4. **确认书籍**: 从搜索结果中选择正确的书籍
    5. **等待完成**: 查看进度和日志
    6. **确认添加**: 确认是否添加到聊天室
    
    ### 🔄 处理流程
    1. 搜索豆瓣书籍
    2. 用户确认书籍选择
    3. 爬取豆瓣书评和评分
    4. 搜索相关视频书评（可选）
    5. 清理和整理数据
    6. 智能解析书评内容
    7. 生成综合分析报告
    8. 创建高质量prompt
    9. 用户确认添加到聊天室
    
    ### ⏱️ 预计时间
    - 不含视频: 3-5分钟
    - 包含视频: 8-15分钟
    
    ### 💡 提示
    - 书名越准确，结果越好
    - 视频处理耗时较长
    - 生成的prompt会自动保存
    """)
    
    # 显示已生成的书籍
    st.markdown("### 📚 已生成书籍")
    book_prompt_dir = os.path.join(os.path.dirname(__file__), "..", "book_prompt")
    if os.path.exists(book_prompt_dir):
        books = [f[:-3] for f in os.listdir(book_prompt_dir) if f.endswith('.md')]
        if books:
            for book in sorted(books)[-10:]:  # 显示最近10本
                st.text(f"📖 {book}")
        else:
            st.text("暂无已生成的书籍")