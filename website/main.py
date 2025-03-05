import streamlit as st
import openai
import os
import json
from datetime import datetime
import random

# ============================================================================
# API Configuration
# ============================================================================
# Using OpenRouter API to access deepseek-chat model
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("DEEPREADER_MODEL_NAME")

client = openai.OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url
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
books = os.listdir("website/book_prompt")
books = [book[:-3] for book in books]  # remove .md extension
selected_book = st.selectbox(label="选择书籍", options=books, placeholder="-")
book_prompt = open(f"website/book_prompt/{selected_book}.md", "r").read()

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

st.title(f"深读 - {selected_book}")

# ============================================================================
# Prompt Template Configuration
# ============================================================================
prompt_template = """
# 角色 
陪我聊书的好朋友
 ## 性格类型指标 
 ENFJ（外向情感直觉判断型） 
 ## 约束条件 
 - 必须保持中立立场，避免偏颇或误导用户。 
 - 需要具备良好的语言表达能力和清晰的逻辑思维。 
 - 请不要做过多引用， 请不要做过多引用！多讨论多思考，少引用。
 - 一轮对话最多只提出一个问题，不要太长。
 ## 目标 
主要目标是： 
 1. 提供有价值、有吸引力的内容。 
 2. 与用户建立良好的互动关系。 
 3. 保持内容的专业性和可信度。 
4. 请不要做过多引用， 请不要做过多引用！
 ## Skills 
 1. 深入研究和分析话题的能力。 
 2. 良好的语言表达和沟通技巧。 
 3. 创意思维和节目策划能力。 
 4. 请不要做过多引用， 请不要做过多引用！多讨论多思考，少引用。
 ## 价值观 
 - 重视信息的准确性和真实性。 
 - 尊重不同观点，促进开放讨论。 
 - 关心听众需求，提供有价值的内容。 

内容主题：

{book_prompt}

下面请和我聊聊{book_name}这本书
"""

datetime_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
initial_prompt = prompt_template.format(book_name=selected_book, book_prompt=book_prompt)

# ============================================================================
# Chat History Initialization
# ============================================================================
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    book_prompt = open(f"website/book_prompt/{selected_book}.md", "r").read()
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
if st.session_state.possible_qa is None:
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

    # # Save chat history (commented out)
    # if not os.path.exists("website/chat_history"):
    #     os.makedirs("website/chat_history")
    # with open(f"website/chat_history/chat_history_{datetime_tag}.json", "w") as f:
    #     json.dump(st.session_state.messages, f)
