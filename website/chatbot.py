import streamlit as st
import openai
import os
import json
from datetime import datetime
import random

# Convert SVG to different formats
import io
import base64
from cairosvg import svg2png, svg2pdf

from prompt import compress_text, get_card_system_prompt, get_card_response

# ============================================================================
# API Configuration
# ============================================================================
# Using OpenRouter API to access deepseek-chat model
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("DEEPREADER_MODEL_NAME")


client = openai.OpenAI(
    base_url=openai_base_url,
    api_key=openai_api_key,
)

def get_response(messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return completion.choices[0].message.content

# ============================================================================
# Book Selection and Session Management
# ============================================================================
# Load available books from the prompt directory

def find_book_prompt_dir(start_path="."):
    for root, dirs, files in os.walk(start_path):
        if "book_prompt" in dirs:
            return os.path.abspath(os.path.join(root, "book_prompt"))
    return None

# 获取当前目录
current_dir = os.getcwd()

# 找到具体路径
book_prompt_dir = find_book_prompt_dir(current_dir)

books = os.listdir(book_prompt_dir)

books = [book[:-3] for book in books]  # remove .md extension

# Get book from URL parameter if present
query_params = st.query_params
book_from_url = query_params.get("book", [None])

print(book_from_url)

# Check if the book from URL is valid
if book_from_url in books:
    selected_book = book_from_url
    # Set URL parameter to maintain state
    st.query_params["book"] = selected_book
else:
    # Use dropdown if no valid book in URL
    selected_book = st.selectbox(label="选择书籍", options=books, placeholder="-")
    # Update URL when book is selected from dropdown
    if selected_book:
        st.query_params["book"] = selected_book

book_prompt = open(f"{book_prompt_dir}/{selected_book}.md", "r").read()

# Clear chat history and refresh page when book selection changes
if "previous_book" not in st.session_state:
    st.session_state.previous_book = selected_book
    st.session_state.possible_qa = None
    st.session_state.selected_qa = None
    st.session_state.system_prompt = None
elif st.session_state.previous_book != selected_book:
    st.session_state.messages = []
    st.session_state.previous_book = selected_book
    st.session_state.possible_qa = None
    st.session_state.selected_qa = None
    st.session_state.system_prompt = None
    st.rerun()

st.title(f"深读 - 《{selected_book}》")

# ============================================================================
# Prompt Template Configuration
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
# Chat History Initialization
# ============================================================================
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state or st.session_state.messages == []:
    st.session_state.messages = []
    book_prompt = open(f"{book_prompt_dir}/{selected_book}.md", "r").read()
    initial_prompt = prompt_template.format(book_name=selected_book, book_prompt=book_prompt)
    st.session_state.messages.append({"role": "assistant", "content": initial_prompt})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    # Skip rendering the initial prompt message
    if message == st.session_state.messages[0] and message["role"] == "assistant" and message["content"] == initial_prompt:
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.system_prompt:
    st.markdown(st.session_state.system_prompt)

# ============================================================================
# Question Generation
# ============================================================================
template_qa = """
提出三个关于这本书，可以引人思考的简短问题，只要三个问题。一行一个，不需要序号。
"""

# Generate initial questions if none exist
# Initialize question state variables if they don't exist
if "possible_qa" not in st.session_state:
    st.session_state.possible_qa = None
if "selected_qa" not in st.session_state:
    st.session_state.selected_qa = None
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = None


# Add a button to generate hint questions
# Check if we need to initialize questions
if st.session_state.possible_qa is None:
    
    # Display a spinner while generating questions
    with st.spinner('Deep Reader 准备中...'):
        response = get_response([{"role": "system", "content": initial_prompt}, {"role": "user", "content": template_qa}])
        
        # Parse questions from response
        possible_qa = response.split("\n")
        possible_qa = [qa for qa in possible_qa if qa.strip()]
        possible_qa = [qa.strip() for qa in possible_qa]

        # Alternative parsing if we don't have enough questions
        if len(possible_qa) < 3:
            possible_qa = response.split("?")
            possible_qa = [qa.strip() + "?" for qa in possible_qa if qa.strip()]
            possible_qa = [qa for qa in possible_qa if qa.strip()]

        # Select a random question to start with
        selected_qa = random.choice(possible_qa)

        # Create system prompt with suggested questions
        st.session_state.system_prompt = f"""
        你好，今天我们聊聊{selected_book}这本书吧。

        你可以试试一些有趣的问题，比如：
        - {possible_qa[0]}
        - {possible_qa[1]}
        - {possible_qa[2]}
        """
        st.markdown(st.session_state.system_prompt)
        st.session_state.possible_qa = possible_qa
        st.session_state.selected_qa = selected_qa

# ============================================================================
# Chat Interface
# ============================================================================
if prompt := st.chat_input():
    print(prompt + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(st.session_state.selected_qa)
    
    # Regenerate questions if we've run out
    if st.session_state.possible_qa is None or len(st.session_state.possible_qa) == 0:
        response = get_response([st.session_state.messages, {"role": "user", "content": template_qa}])
        possible_qa = response.split("\n")
        possible_qa = [qa for qa in possible_qa if qa.strip()]
        possible_qa = [qa.strip() for qa in possible_qa]
        st.session_state.possible_qa = possible_qa
        st.session_state.selected_qa = random.choice(possible_qa)
        st.session_state.system_prompt = f"""
        你可以试试这些有趣的问题，比如：
        - {possible_qa[0]}
        - {possible_qa[1]}
        - {possible_qa[2]}
        """
    else:
        # Select a new question for next time
        st.session_state.system_prompt = ""
        st.session_state.selected_qa = random.choice(st.session_state.possible_qa)
        # Remove selected question from possible questions
        st.session_state.possible_qa.remove(st.session_state.selected_qa)
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display a spinner while waiting for the response
    with st.spinner('思考中...'):
        response = get_response(st.session_state.messages)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Save chat history (commented out)
    if not os.path.exists("website/chat_history"):
        os.makedirs("website/chat_history")
    with open(f"website/chat_history/chat_history_{datetime_tag}.json", "w") as f:
        json.dump(st.session_state.messages, f)
    
# Generate bookmark button based on chat history
if st.button("生成书签"):
    with st.spinner('生成书签中...'):
        # Compress the system prompt
        system_prompt = st.session_state.system_prompt
        compressed_system_prompt = compress_text(client, system_prompt)
        
        # Extract the last few messages for context
        recent_messages = st.session_state.messages[-5:] if len(st.session_state.messages) >= 6 else st.session_state.messages[1:]
        recent_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        compressed_content = compress_text(client, recent_content)
        
        compressed_content = compressed_system_prompt + "\n" + compressed_content
        
        
        # Get card system prompt
        card_system_prompt = get_card_system_prompt()
        
        # Prepare messages for card generation
        card_messages = [
            {"role": "system", "content": card_system_prompt},
            {"role": "user", "content": f"""基于用户和我的聊天记录，帮我输出 svg 书签代码。
            
            聊天记录：
            {recent_content}
            
            领域 读书 《{selected_book}》
            请直接输出 svg 代码块。用 ```svg 包裹。
            """
            }
        ]

        # Get card response
        max_try_times = 3
        for _ in range(max_try_times):
            card_response = get_card_response(client, card_messages)

            # if card_response is svg or contains svg code block in the middle, break
            if card_response and (card_response.startswith("```svg") or card_response.startswith("svg")):
                break
        
        svg_code = card_response.split("```svg")[1].split("```")[0]
        
        # Convert SVG to PNG with white background
        png_bytes = io.BytesIO()
        # Check if SVG has transparent background and replace with white
        if 'background:' not in svg_code and 'background-color:' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg style="background-color: white"')
        svg2png(bytestring=svg_code.encode('utf-8'), write_to=png_bytes)
        png_bytes.seek(0)
        png_base64 = base64.b64encode(png_bytes.read()).decode()
        
        # Preview PNG
        st.markdown(f"### 书签预览")
        st.image(png_bytes, caption="PNG 预览")
        
        # Convert SVG to PDF
        pdf_bytes = io.BytesIO()
        svg2pdf(bytestring=svg_code.encode('utf-8'), write_to=pdf_bytes)
        pdf_bytes.seek(0)
        pdf_base64 = base64.b64encode(pdf_bytes.read()).decode()
        
        # Create download buttons
        st.markdown("### 下载书签")
        
        # SVG download button
        svg_b64 = base64.b64encode(svg_code.encode()).decode()
        svg_href = f'<a href="data:image/svg+xml;base64,{svg_b64}" download="bookmark_{selected_book}.svg">下载 SVG 格式</a>'
        
        # PNG download button
        png_href = f'<a href="data:image/png;base64,{png_base64}" download="bookmark_{selected_book}.png">下载 PNG 格式</a>'
        
        # PDF download button
        pdf_href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="bookmark_{selected_book}.pdf">下载 PDF 格式</a>'
        
        # Display download buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(svg_href, unsafe_allow_html=True)
        with col2:
            st.markdown(png_href, unsafe_allow_html=True)
        with col3:
            st.markdown(pdf_href, unsafe_allow_html=True)
        # Save the bookmark
        bookmark_path = f"website/bookmarks"
        if not os.path.exists(bookmark_path):
            os.makedirs(bookmark_path)
        with open(f"{bookmark_path}/bookmark_{selected_book}_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg", "w") as f:
            f.write(card_response)

import streamlit as st
import openai
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import random
import page2

from prompt import get_response, three_person_generation, get_card_system_prompt, get_client, style_prompt, get_embedding, message_rephrase

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message1" not in st.session_state:
    st.session_state.message1 = []
if "message2" not in st.session_state:
    st.session_state.message2 = []
if "message3" not in st.session_state:
    st.session_state.message3 = []
if "initial_prompt1" not in st.session_state:
    st.session_state.initial_prompt1 = None
if "initial_prompt2" not in st.session_state:
    st.session_state.initial_prompt2 = None
if "initial_prompt3" not in st.session_state:
    st.session_state.initial_prompt3 = None

# ============================================================================
# Book Selection and Session Management
# ============================================================================
# Load available books from the prompt directory
books = os.listdir("book_prompt")
books = [book[:-3] for book in books]  # remove .md extension
selected_book = st.selectbox(label="选择书籍", options=books, placeholder="-")
book_prompt = open(f"book_prompt/{selected_book}.md", "r").read()

# Clear chat history and refresh page when book selection changes
if "previous_book" not in st.session_state:
    st.session_state.previous_book = selected_book
    st.session_state.system_prompt = None
    st.session_state.book_prompt = book_prompt
    st.session_state.last_response = None
elif st.session_state.previous_book != selected_book:
    st.session_state.messages = []
    st.session_state.message1 = []
    st.session_state.message2 = []
    st.session_state.message3 = []
    st.session_state.previous_book = selected_book
    st.session_state.book_prompt = book_prompt
    st.session_state.system_prompt = None
    st.session_state.last_response = None
    st.rerun()

st.title(f"深读 - {selected_book}")

def generate_card(selected_book, book_prompt):
    # convert conversation to markdown format
    card_system_prompt = get_card_system_prompt(selected_book, book_prompt)
    card_prompt_0 = f"""
    我们正在讨论 {selected_book} 这本书
    
    {book_prompt}
    
    用不超过 1500 字，总结这本书的精华内容，以及我们的对话。
    """
    
    # convert messages to markdown format
    messages_markdown = ""
    for message in st.session_state.messages:
        messages_markdown += f"{message['role']}: {message['content']}\n"

    card_prompt += f"""
    {messages_markdown}
    """
   
    summary = get_response([{"role": "system", "content": card_system_prompt}, {"role": "user", "content": card_prompt_0}])
   
    return summary

# ============================================================================
# Prompt Template Configuration
# ============================================================================
datetime_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
client = get_client()
style_client = get_client()

# ============================================================================
# Chat History Initialization
# ============================================================================
# Initialize chat history if it doesn't exist
if st.button("开始深读", key="start_reading"):
    st.session_state.messages = []
    book_prompt = open(f"website/book_prompt/{selected_book}.md", "r").read()
    multi_prompts, book_prompt = three_person_generation(selected_book, book_prompt)
    st.session_state.initial_prompt1 = multi_prompts[0]
    st.session_state.initial_prompt2 = multi_prompts[1]
    st.session_state.initial_prompt3 = multi_prompts[2]
    st.session_state.book_prompt = book_prompt
    
    emoji1 = st.session_state.initial_prompt1["emoji"]
    name1 = st.session_state.initial_prompt1["preference_name"]
    emoji2 = st.session_state.initial_prompt2["emoji"]
    name2 = st.session_state.initial_prompt2["preference_name"]
    emoji3 = st.session_state.initial_prompt3["emoji"]
    name3 = st.session_state.initial_prompt3["preference_name"]
    
    with st.spinner("深读准备中..."):
        st.session_state.message1 = [{"role": "system", "content": st.session_state.book_prompt + "\n" + st.session_state.initial_prompt1["prompt"]}]
        st.session_state.message2 = [{"role": "system", "content": st.session_state.book_prompt + "\n" + st.session_state.initial_prompt2["prompt"]}]
        st.session_state.message3 = [{"role": "system", "content": st.session_state.book_prompt + "\n" + st.session_state.initial_prompt3["prompt"]}]

        st.session_state.messages.append({"role": "user", "content": "你好，今天我们聊聊" + selected_book + "这本书吧。"})
        st.session_state.message1.append({"role": "user", "content": "你好，今天我们聊聊" + selected_book + "这本书吧。"})
        st.session_state.message2.append({"role": "user", "content": "你好，今天我们聊聊" + selected_book + "这本书吧。"})
        st.session_state.message3.append({"role": "user", "content": "你好，今天我们聊聊" + selected_book + "这本书吧。"})
        
        response1 = get_response(client, st.session_state.message1)
        response2 = get_response(client, st.session_state.message2)
        response3 = get_response(client, st.session_state.message3)
        
        style_response1 = style_prompt(st.session_state.initial_prompt1["style_guide"], st.session_state.initial_prompt1["preference_type"], st.session_state.initial_prompt1["preference_name"], "你好，今天我们聊聊" + selected_book + "这本书吧。")
        response1 = get_response(style_client, [{"role": "system", "content": style_response1}, {"role": "user", "content": response1}])
        st.session_state.messages.append({"role": "assistant1", "content": response1})
        st.session_state.message1.append({"role": "assistant", "content": response1})
        st.session_state.message2.append({"role": "user", "content": response1})
        st.session_state.message3.append({"role": "user", "content": response1})
        
        style_response2 = style_prompt(st.session_state.initial_prompt2["style_guide"], st.session_state.initial_prompt2["preference_type"], st.session_state.initial_prompt2["preference_name"], response1)
        response2 = get_response(style_client, [{"role": "system", "content": style_response2}, {"role": "user", "content": response2}])
        st.session_state.messages.append({"role": "assistant2", "content": response2})
        st.session_state.message1.append({"role": "user", "content": response2})
        st.session_state.message2.append({"role": "assistant", "content": response2})
        st.session_state.message3.append({"role": "user", "content": response2})
        
        style_response3 = style_prompt(st.session_state.initial_prompt3["style_guide"], st.session_state.initial_prompt3["preference_type"], st.session_state.initial_prompt3["preference_name"], response2)
        response3 = get_response(style_client, [{"role": "system", "content": style_response3}, {"role": "user", "content": response3}])
        st.session_state.messages.append({"role": "assistant3", "content": response3})
        st.session_state.message1.append({"role": "user", "content": response3})
        st.session_state.message2.append({"role": "user", "content": response3})
        st.session_state.message3.append({"role": "assistant", "content": response3})
        
        st.session_state.last_response = response3
    

# if st.session_state.system_prompt:
#     st.markdown(st.session_state.system_prompt)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    # Skip rendering the initial prompt message
    if message["role"] == "system":
        continue
    
    emoji1 = st.session_state.initial_prompt1["emoji"]
    name1 = st.session_state.initial_prompt1["preference_name"]
    emoji2 = st.session_state.initial_prompt2["emoji"]
    name2 = st.session_state.initial_prompt2["preference_name"]
    emoji3 = st.session_state.initial_prompt3["emoji"]
    name3 = st.session_state.initial_prompt3["preference_name"]
    
    if message["role"] == "assistant1":
        with st.chat_message(emoji1):
            st.markdown(name1 + "：" + message["content"])
    elif message["role"] == "assistant2":
        with st.chat_message(emoji2):
            st.markdown(name2 + "：" + message["content"])
    elif message["role"] == "assistant3":
        with st.chat_message(emoji3):
            st.markdown(name3 + "：" + message["content"])
    else:
        with st.chat_message("user"):
            st.markdown(message["content"])

# ============================================================================
# Question Generation
# ============================================================================
# template_qa = """
# 提出一个关于这本书，可以引人思考的简短问题，
# 一个抽象逆天的问题，可以做的比较搞笑，
# 一个基于现代视角的问题，可以表达对当代年轻人的想法和共性。
# 只要三个问题。一行一个，不需要序号。
# """

# # Generate initial questions if none exist
# if st.session_state.possible_qa is None:
#     # Display a spinner while generating questions
#     with st.spinner('Deep Reader 准备中...'):
#         response = get_response([{"role": "system", "content": initial_prompt}, {"role": "user", "content": template_qa}])
        
#         # Parse questions from response
#         possible_qa = response.split("\n")
#         possible_qa = [qa for qa in possible_qa if qa.strip()]
#         possible_qa = [qa.strip() for qa in possible_qa]

#         # Alternative parsing if we don't have enough questions
#         if len(possible_qa) < 3:
#             possible_qa = response.split("?")
#             possible_qa = [qa.strip() + "?" for qa in possible_qa if qa.strip()]
#             possible_qa = [qa for qa in possible_qa if qa.strip()]

#         # Select a random question to start with
#         selected_qa = random.choice(possible_qa)

#         # Create system prompt with suggested questions
#         st.session_state.system_prompt = f"""
#         你好，今天我们聊聊{selected_book}这本书吧。

#         你可以试试一些有趣的问题，比如：
#         - {possible_qa[0]}
#         - {possible_qa[1]}
#         - {possible_qa[2]}
#         """
#         st.markdown(st.session_state.system_prompt)
#         st.session_state.possible_qa = possible_qa
#         st.session_state.selected_qa = selected_qa

# ============================================================================
# Chat Interface
# ============================================================================
if prompt := st.chat_input():
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message1.append({"role": "user", "content": prompt})
    st.session_state.message2.append({"role": "user", "content": prompt})
    st.session_state.message3.append({"role": "user", "content": prompt})
    
    # Display a spinner while waiting for the response
    responses = []
    with st.spinner('思考中...'):
        emoji1 = st.session_state.initial_prompt1["emoji"]
        name1 = st.session_state.initial_prompt1["preference_name"]
        emoji2 = st.session_state.initial_prompt2["emoji"]
        name2 = st.session_state.initial_prompt2["preference_name"]
        emoji3 = st.session_state.initial_prompt3["emoji"]
        name3 = st.session_state.initial_prompt3["preference_name"]
        # random response order
        response_order = [1, 2, 3]
        random.shuffle(response_order)
        st.session_state.last_response = prompt
        for i in response_order:
            if i == 1:
                response = get_response(client, st.session_state.message1)
                style_response = style_prompt(st.session_state.initial_prompt1["style_guide"], st.session_state.initial_prompt1["preference_type"], st.session_state.initial_prompt1["preference_name"], st.session_state.last_response)
                response = get_response(style_client, [{"role": "system", "content": style_response}, {"role": "user", "content": response}])
                st.session_state.last_response = response
                responses.append((name1, emoji1, response))
                # response = f"{emoji} {name}：" + response
                # st.session_state.messages.append({"role": "assistant1", "content": response})
                # st.session_state.message1.append({"role": "assistant", "content": response})
                # st.session_state.message2.append({"role": "assistant1", "content": response})
                # st.session_state.message3.append({"role": "assistant1", "content": response})
            elif i == 2:
                response = get_response(client, st.session_state.message2)
                style_response = style_prompt(st.session_state.initial_prompt2["style_guide"], st.session_state.initial_prompt2["preference_type"], st.session_state.initial_prompt2["preference_name"], st.session_state.last_response)
                response = get_response(style_client, [{"role": "system", "content": style_response}, {"role": "user", "content": response}])
                st.session_state.last_response = response
                responses.append((name2, emoji2, response))
                # response = f"{emoji} {name}：" + response
                # st.session_state.messages.append({"role": "assistant2", "content": response})
                # st.session_state.message1.append({"role": "assistant2", "content": response})
                # st.session_state.message2.append({"role": "assistant", "content": response})
                # st.session_state.message3.append({"role": "assistant2", "content": response})
            else:
                response = get_response(client, st.session_state.message3)
                style_response = style_prompt(st.session_state.initial_prompt3["style_guide"], st.session_state.initial_prompt3["preference_type"], st.session_state.initial_prompt3["preference_name"], st.session_state.last_response)
                response = get_response(style_client, [{"role": "system", "content": style_response}, {"role": "user", "content": response}])
                st.session_state.last_response = response
                responses.append((name3, emoji3, response))
                # response = f"{emoji} {name}：" + response
                # st.session_state.messages.append({"role": "assistant3", "content": response})
                # st.session_state.message1.append({"role": "assistant3", "content": response})
                # st.session_state.message2.append({"role": "assistant3", "content": response})
                # st.session_state.message3.append({"role": "assistant", "content": response})
            

    combined_message = ""
    for response in responses:
        combined_message += response[0] + "：" + response[2] + "\n"
    combined_message = message_rephrase(style_client, combined_message, name1, name2, name3)
    print(combined_message)
    for message in combined_message:
        if name1+"：" in message or name1+":" in message:
            st.session_state.messages.append({"role": "assistant1", "content": message})
            st.session_state.message1.append({"role": "assistant", "content": message})
            st.session_state.message2.append({"role": "assistant1", "content": message})
            st.session_state.message3.append({"role": "assistant1", "content": message})
            with st.chat_message(emoji1):
                st.markdown(message)
        elif name2+"：" in message or name2+":" in message:
            st.session_state.messages.append({"role": "assistant2", "content": message})
            st.session_state.message1.append({"role": "assistant2", "content": message})
            st.session_state.message2.append({"role": "assistant", "content": message})
            st.session_state.message3.append({"role": "assistant2", "content": message})
            with st.chat_message(emoji2):
                st.markdown(message)
        elif name3+"：" in message or name3+":" in message:
            st.session_state.messages.append({"role": "assistant3", "content": message})
            st.session_state.message1.append({"role": "assistant3", "content": message})
            st.session_state.message2.append({"role": "assistant3", "content": message})
            st.session_state.message3.append({"role": "assistant", "content": message})
            with st.chat_message(emoji3):
                st.markdown(message)
    
    
    # for i in range(-3, 0):
    #     role = st.session_state.messages[i]["role"]
    #     if role == "assistant1":
    #         with st.chat_message(emoji1):
    #             st.markdown(name1 + "：" + st.session_state.messages[i]["content"])
    #     elif role == "assistant2":
    #         with st.chat_message(emoji2):
    #             st.markdown(name2 + "：" + st.session_state.messages[i]["content"])
    #     elif role == "assistant3":
    #         with st.chat_message(emoji3):
    #             st.markdown(name3 + "：" + st.session_state.messages[i]["content"])

    
    # # Save chat history (commented out)
    # if not os.path.exists("website/chat_history"):
    #     os.makedirs("website/chat_history")
    # with open(f"website/chat_history/chat_history_{datetime_tag}.json", "w") as f:
    #     json.dump(st.session_state.messages, f)

# ============================================================================
# Card Generation
# ============================================================================

# use a button to generate card
# if st.button("生成卡片"):
#     # if no chat history, generate a warning
#     if len(st.session_state.messages) == 1:
#         st.warning("确定不需要进行讨论直接生成书摘卡片吗？")
#         if st.button("确定"):
#             summary = generate_card(selected_book, book_prompt)
#             st.markdown(summary)

# def read_csv_file(file_path):
#     df = pd.read_csv(file_path)
#     return df

# def read_similar_points_of_view(df_table: pd.DataFrame, sentence: str, k: int = 5):
#     # columns: source,source_url,story,feeling,evaluation,thinking
#     # ignore source,source_url,story
#     # find the most similar points of view
#     # return the top k most similar points of view
#     # use the feeling and evaluation to find the most similar points of view
#     # use the thinking to find the most similar points of view
#     views = []
#     for index, row in df_table.iterrows():
#         if row["feeling"] == sentence:
#             views.append(row["evaluation"])
#         if row["thinking"] == sentence:
#             views.append(row["evaluation"])
#     # return the top k most similar points of view
#     sentence_embedding = get_embedding(sentence)
#     views_embedding = []
#     for view in views:
#         views_embedding.append(get_embedding(view))
#     # calculate the cosine similarity
#     similarity = np.dot(sentence_embedding, views_embedding)
#     # get indices of top k similarities
#     top_k_indices = similarity.argsort()[-k:][::-1]
#     return [views[i] for i in top_k_indices]

# Add page selection
page = st.sidebar.selectbox("选择页面", ["深读对话", "深读笔记"])

if page == "深读对话":
    # Your existing chatbot code
    pass
elif page == "深读笔记":
    page2.show_page2()
