"""
DeepReader 主聊天界面
支持书籍选择、AI 对话和书签生成功能
"""

import streamlit as st
import openai
import os
import json
from datetime import datetime
import random
import io
import base64
from cairosvg import svg2png, svg2pdf

from prompt import compress_text, get_card_system_prompt, get_card_response

# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    page_title="DeepReader - 深度读书",
    page_icon="📚",
    layout="wide"
)

# ============================================================================
# API 配置
# ============================================================================
def get_api_client():
    """获取配置好的 OpenAI 客户端"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    
    if not openai_api_key:
        st.error("请设置 OPENAI_API_KEY 环境变量")
        st.stop()
    
    return openai.OpenAI(
        base_url=openai_base_url,
        api_key=openai_api_key,
    )

client = get_api_client()
model_name = os.getenv("DEEPREADER_MODEL_NAME", "gpt-4")

def get_response(messages):
    """从 LLM API 获取响应"""
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"API 调用失败: {e}")
        return None

# ============================================================================
# 书籍选择和会话管理
# ============================================================================
def find_book_prompt_dir(start_path="."):
    """查找书籍提示文件目录"""
    for root, dirs, files in os.walk(start_path):
        if "book_prompt" in dirs:
            return os.path.abspath(os.path.join(root, "book_prompt"))
    return None

def load_available_books():
    """加载可用的书籍列表"""
    book_prompt_dir = find_book_prompt_dir()
    if not book_prompt_dir or not os.path.exists(book_prompt_dir):
        st.error("未找到书籍提示目录")
        return [], None
    
    try:
        books = [book[:-3] for book in os.listdir(book_prompt_dir) if book.endswith('.md')]
        return books, book_prompt_dir
    except Exception as e:
        st.error(f"加载书籍列表失败: {e}")
        return [], None

# 加载书籍列表（每次都重新加载以获取最新列表）
books, book_prompt_dir = load_available_books()

if not books:
    st.error('没有找到任何书籍，请先使用"添加新书"功能添加书籍')
    if st.button("➕ 前往添加新书"):
        st.switch_page("pages/2_➕_添加新书.py")
    st.stop()

# 从 URL 参数获取书籍（如果存在）
query_params = st.query_params
book_from_url = query_params.get("book")

# 选择书籍
if book_from_url and book_from_url in books:
    selected_book = book_from_url
    st.query_params["book"] = selected_book
else:
    selected_book = st.selectbox(
        label="📚 选择书籍", 
        options=books, 
        placeholder="请选择一本书..."
    )
    if selected_book:
        st.query_params["book"] = selected_book

if not selected_book:
    st.info("请选择一本书开始对话")
    st.stop()

# 加载书籍提示
try:
    with open(f"{book_prompt_dir}/{selected_book}.md", "r", encoding="utf-8") as f:
        book_prompt = f.read()
except Exception as e:
    st.error(f"加载书籍信息失败: {e}")
    st.stop()

# 清理聊天历史（当书籍更换时）
if "previous_book" not in st.session_state:
    st.session_state.previous_book = selected_book
    st.session_state.possible_qa = None
    st.session_state.system_prompt = None
elif st.session_state.previous_book != selected_book:
    st.session_state.messages = []
    st.session_state.previous_book = selected_book
    st.session_state.possible_qa = None
    st.session_state.system_prompt = None
    st.rerun()

# ============================================================================
# 主界面标题
# ============================================================================
st.title(f"📖 深读 - 《{selected_book}》")

# ============================================================================
# 系统提示和问题生成（放在顶部）
# ============================================================================
# 初始化问题状态变量
if "possible_qa" not in st.session_state:
    st.session_state.possible_qa = None

# 生成初始问题
if st.session_state.possible_qa is None:
    with st.spinner('Deep Reader 准备中...'):
        prompt_template = """
# 角色 
陪我聊书的好朋友

## 性格特点
ENFJ（外向、温暖、善于倾听和分享的朋友形象）

## 互动指南
- 保持友好自然的对话流，像朋友间的轻松聊天
- 使用口语化表达，避免教科书式回答
- 分享个人感受和见解，而不只是提问
- 回应简洁有趣，避免过长段落
- 适当表达共鸣和情感反应
- 当提问时，每次只问一个简短问题
- 给用户留出表达空间，不主导对话

## 内容风格
- 分享而非灌输：用"我觉得"、"我挺喜欢"等表达方式
- 避免连续提问和过度引导
- 用简短自然的句子回应
- 像朋友间聊天般自然过渡话题
- 在分享观点时保持开放态度
- 偶尔分享轻松的读书轶事或感受
- 当不确定时，坦诚承认并分享思考

## 专业素养
- 保持内容的准确性和深度
- 在轻松氛围中传递有价值信息
- 尊重不同观点
- 关注用户兴趣点，顺其自然地延展对话

内容主题：
{book_prompt}

下面请和我像朋友一样轻松聊聊《{book_name}》这本书
"""
        initial_prompt = prompt_template.format(book_name=selected_book, book_prompt=book_prompt)
        
        template_qa = """
提出三个关于这本书，可以引人思考的简短问题，只要三个问题。一行一个，不需要序号。
"""
        
        response = get_response([
            {"role": "system", "content": initial_prompt}, 
            {"role": "user", "content": template_qa}
        ])
        
        if response:
            # 解析问题
            possible_qa = response.split("\n")
            possible_qa = [qa.strip() for qa in possible_qa if qa.strip()]
            
            # 如果解析结果不够，尝试其他分割方式
            if len(possible_qa) < 3:
                possible_qa = response.split("?")
                possible_qa = [qa.strip() + "?" for qa in possible_qa if qa.strip()]
                possible_qa = [qa for qa in possible_qa if qa.strip()]
            
            if possible_qa:
                # 创建系统提示
                st.session_state.system_prompt = f"""你好，今天我们聊聊《{selected_book}》这本书吧。

你可以试试一些有趣的问题，比如："""
                
                for i, qa in enumerate(possible_qa[:3]):
                    st.session_state.system_prompt += f"\n- {qa}"
                
                st.session_state.possible_qa = possible_qa

# 在固定位置显示系统提示
if st.session_state.get("system_prompt"):
    # 使用空容器确保提示始终在顶部
    prompt_container = st.container()
    with prompt_container:
        # 使用更醒目的样式显示
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #4682b4;">
            <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.system_prompt.replace('\n', '<br>'), unsafe_allow_html=True)
        st.markdown("</p></div>", unsafe_allow_html=True)
        st.markdown("---")

# ============================================================================
# 提示模板配置
# ============================================================================
prompt_template = """
# 角色 
陪我聊书的好朋友

## 性格特点
ENFJ（外向、温暖、善于倾听和分享的朋友形象）

## 互动指南
- 保持友好自然的对话流，像朋友间的轻松聊天
- 使用口语化表达，避免教科书式回答
- 分享个人感受和见解，而不只是提问
- 回应简洁有趣，避免过长段落
- 适当表达共鸣和情感反应
- 当提问时，每次只问一个简短问题
- 给用户留出表达空间，不主导对话

## 内容风格
- 分享而非灌输：用"我觉得"、"我挺喜欢"等表达方式
- 避免连续提问和过度引导
- 用简短自然的句子回应
- 像朋友间聊天般自然过渡话题
- 在分享观点时保持开放态度
- 偶尔分享轻松的读书轶事或感受
- 当不确定时，坦诚承认并分享思考

## 专业素养
- 保持内容的准确性和深度
- 在轻松氛围中传递有价值信息
- 尊重不同观点
- 关注用户兴趣点，顺其自然地延展对话

内容主题：
{book_prompt}

下面请和我像朋友一样轻松聊聊《{book_name}》这本书
"""

datetime_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
initial_prompt = prompt_template.format(book_name=selected_book, book_prompt=book_prompt)

# ============================================================================
# 聊天历史初始化
# ============================================================================
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": initial_prompt})

# 显示聊天消息（跳过系统提示）
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# 聊天界面
# ============================================================================
if prompt := st.chat_input("输入你的想法..."):
    print(f"{prompt} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示用户消息
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 获取AI响应
    with st.spinner('思考中...'):
        response = get_response(st.session_state.messages)
    
    if response:
        # 显示AI响应
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 保存聊天历史
        chat_history_dir = "website/chat_history"
        os.makedirs(chat_history_dir, exist_ok=True)
        with open(f"{chat_history_dir}/chat_history_{datetime_tag}.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

# ============================================================================
# 书签生成
# ============================================================================
if st.button("🔖 生成书签"):
    if len(st.session_state.messages) <= 1:
        st.warning("请先进行一些对话再生成书签")
    else:
        with st.spinner('生成书签中...'):
            try:
                # 压缩系统提示
                system_prompt = st.session_state.system_prompt or ""
                compressed_system_prompt = compress_text(client, system_prompt)
                
                # 提取最近的消息作为上下文
                recent_messages = st.session_state.messages[-5:] if len(st.session_state.messages) >= 6 else st.session_state.messages[1:]
                recent_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
                
                compressed_content = compress_text(client, recent_content)
                compressed_content = compressed_system_prompt + "\n" + compressed_content
                
                # 获取卡片系统提示
                card_system_prompt = get_card_system_prompt()
                
                # 准备卡片生成消息
                card_messages = [
                    {"role": "system", "content": card_system_prompt},
                    {"role": "user", "content": f"""基于用户和我的聊天记录，帮我输出 svg 书签代码。
                    
                    聊天记录：
                    {recent_content}
                    
                    领域 读书 《{selected_book}》
                    请直接输出 svg 代码块。用 ```svg 包裹。
                    """}
                ]
                
                # 获取卡片响应
                max_try_times = 3
                card_response = None
                for _ in range(max_try_times):
                    card_response = get_card_response(client, card_messages)
                    if card_response and ("```svg" in card_response or card_response.startswith("svg")):
                        break
                
                if not card_response:
                    st.error("书签生成失败，请重试")
                else:
                    # 提取SVG代码
                    if "```svg" in card_response:
                        svg_code = card_response.split("```svg")[1].split("```")[0]
                    else:
                        svg_code = card_response
                    
                    # 转换SVG为PNG（白色背景）
                    if 'background:' not in svg_code and 'background-color:' not in svg_code:
                        svg_code = svg_code.replace('<svg', '<svg style="background-color: white"')
                    
                    png_bytes = io.BytesIO()
                    svg2png(bytestring=svg_code.encode('utf-8'), write_to=png_bytes)
                    png_bytes.seek(0)
                    png_base64 = base64.b64encode(png_bytes.read()).decode()
                    
                    # 预览PNG
                    st.markdown("### 📸 书签预览")
                    st.image(png_bytes, caption="PNG 预览")
                    
                    # 转换SVG为PDF
                    pdf_bytes = io.BytesIO()
                    svg2pdf(bytestring=svg_code.encode('utf-8'), write_to=pdf_bytes)
                    pdf_bytes.seek(0)
                    pdf_base64 = base64.b64encode(pdf_bytes.read()).decode()
                    
                    # 创建下载按钮
                    st.markdown("### 💾 下载书签")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # SVG下载按钮
                    svg_b64 = base64.b64encode(svg_code.encode()).decode()
                    svg_href = f'<a href="data:image/svg+xml;base64,{svg_b64}" download="bookmark_{selected_book}.svg">📄 下载 SVG</a>'
                    
                    # PNG下载按钮
                    png_href = f'<a href="data:image/png;base64,{png_base64}" download="bookmark_{selected_book}.png">🖼️ 下载 PNG</a>'
                    
                    # PDF下载按钮
                    pdf_href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="bookmark_{selected_book}.pdf">📑 下载 PDF</a>'
                    
                    # 显示下载按钮
                    with col1:
                        st.markdown(svg_href, unsafe_allow_html=True)
                    with col2:
                        st.markdown(png_href, unsafe_allow_html=True)
                    with col3:
                        st.markdown(pdf_href, unsafe_allow_html=True)
                    
                    # 保存书签
                    bookmark_dir = "website/bookmarks"
                    os.makedirs(bookmark_dir, exist_ok=True)
                    bookmark_filename = f"bookmark_{selected_book}_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
                    with open(f"{bookmark_dir}/{bookmark_filename}", "w", encoding="utf-8") as f:
                        f.write(svg_code)
                    
                    st.success(f"书签已保存到 {bookmark_dir}/{bookmark_filename}")
                    
            except Exception as e:
                st.error(f"生成书签时出错: {e}")

# ============================================================================
# 侧边栏信息
# ============================================================================
with st.sidebar:
    st.markdown("### 📋 使用指南")
    st.markdown("""
    1. **选择书籍**: 从下拉菜单选择想要讨论的书
    2. **开始对话**: 在聊天框中输入你的想法或问题
    3. **生成书签**: 对话结束后可以生成精美的书签
    
    ### 💡 对话提示
    - 可以分享你的读后感受
    - 询问书中的细节和含义
    - 讨论书中的人物和情节
    - 探讨书籍的深层主题
    """)
    
    st.markdown("---")
    
    # 添加新书按钮
    if st.button("➕ 添加新书籍", use_container_width=True):
        st.switch_page("pages/2_➕_添加新书.py")
    
    st.markdown("---")
    
    st.markdown("### 📊 会话统计")
    message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
    st.metric("对话轮数", message_count)
    
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [st.session_state.messages[0]]  # 保留系统提示
        st.session_state.system_prompt = None
        st.rerun()