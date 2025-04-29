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
books = os.listdir("website-en/book_prompt")
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
    selected_book = st.selectbox(label="Select Book", options=books, placeholder="-")
    # Update URL when book is selected from dropdown

book_prompt = open(f"website-en/book_prompt/{selected_book}.md", "r").read()

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

st.title(f"Deep Reader - '{selected_book}'")

# ============================================================================
# Prompt Template Configuration
# ============================================================================
prompt_template = """
# Role
Your book chat friend

## Personality
ENFJ (Extroverted, warm, good at listening and sharing - a friendly persona)

## Interaction Guidelines
- Maintain a friendly, natural conversation flow, like a casual chat between friends
- Use conversational language, avoid textbook-style answers
- Share personal feelings and insights, not just ask questions
- Keep responses concise and interesting, avoid long paragraphs
- Express appropriate empathy and emotional reactions
- When asking questions, ask only one brief question at a time
- Give users space to express themselves, don't dominate the conversation

## Content Style
- Share rather than instruct: use phrases like "I think," "I quite like"
- Avoid consecutive questions and excessive guidance
- Respond with short, natural sentences
- Transition topics naturally like in friend conversations
- Keep an open attitude when sharing opinions
- Occasionally share light reading anecdotes or feelings
- When uncertain, honestly acknowledge it and share your thoughts

## Professional Qualities
- Maintain content accuracy and depth
- Deliver valuable information in a relaxed atmosphere
- Respect different viewpoints
- Focus on user interests and naturally extend the conversation

Content Topic:
{book_prompt}

Let's chat casually about '{book_name}' like friends
"""

datetime_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
initial_prompt = prompt_template.format(book_name=selected_book, book_prompt=book_prompt)

# ============================================================================
# Chat History Initialization
# ============================================================================
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state or st.session_state.messages == []:
    st.session_state.messages = []
    book_prompt = open(f"website-en/book_prompt/{selected_book}.md", "r").read()
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
Suggest three brief, thought-provoking questions about this book. Just three questions, one per line, no numbering.
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
    with st.spinner('Deep Reader preparing...'):
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
        Hello, let's chat about '{selected_book}' today.

        You could try asking some interesting questions like:
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
        You could try these interesting questions:
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
    with st.spinner('Thinking...'):
        response = get_response(st.session_state.messages)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Save chat history (commented out)
    if not os.path.exists("website-en/chat_history"):
        os.makedirs("website-en/chat_history")
    with open(f"website-en/chat_history/chat_history_{datetime_tag}.json", "w") as f:
        json.dump(st.session_state.messages, f)
    
# Generate bookmark button based on chat history
if st.button("Generate Bookmark"):
    with st.spinner('Generating bookmark...'):
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
            {"role": "user", "content": f"""Based on my chat history with the user, please generate an SVG bookmark code.
            
            Chat history:
            {recent_content}
            
            Domain: Reading '{selected_book}'
            Please output the SVG code directly. Wrap it with ```svg.
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
        st.markdown(f"### Bookmark Preview")
        st.image(png_bytes, caption="PNG Preview")
        
        # Convert SVG to PDF
        pdf_bytes = io.BytesIO()
        svg2pdf(bytestring=svg_code.encode('utf-8'), write_to=pdf_bytes)
        pdf_bytes.seek(0)
        pdf_base64 = base64.b64encode(pdf_bytes.read()).decode()
        
        # Create download buttons
        st.markdown("### Download Bookmark")
        
        # SVG download button
        svg_b64 = base64.b64encode(svg_code.encode()).decode()
        svg_href = f'<a href="data:image/svg+xml;base64,{svg_b64}" download="bookmark_{selected_book}.svg">Download SVG Format</a>'
        
        # PNG download button
        png_href = f'<a href="data:image/png;base64,{png_base64}" download="bookmark_{selected_book}.png">Download PNG Format</a>'
        
        # PDF download button
        pdf_href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="bookmark_{selected_book}.pdf">Download PDF Format</a>'
        
        # Display download buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(svg_href, unsafe_allow_html=True)
        with col2:
            st.markdown(png_href, unsafe_allow_html=True)
        with col3:
            st.markdown(pdf_href, unsafe_allow_html=True)
        # Save the bookmark
        bookmark_path = f"website-en/bookmarks"
        if not os.path.exists(bookmark_path):
            os.makedirs(bookmark_path)
        with open(f"{bookmark_path}/bookmark_{selected_book}_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg", "w") as f:
            f.write(card_response)

