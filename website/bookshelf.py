import os
import streamlit as st
import autogen
from pathlib import Path
import json
import time

# Set up page configuration
st.set_page_config(
    page_title="DeepReader Bookshelf",
    page_icon="📚",
    layout="wide"
)

# Define paths
BOOK_PROMPT_DIR = Path("website/book_prompt")

# Ensure the book_prompt directory exists
BOOK_PROMPT_DIR.mkdir(exist_ok=True, parents=True)

# Load existing books
def load_existing_books():
    books = []
    for book_file in BOOK_PROMPT_DIR.glob("*.md"):
        book_name = book_file.stem
        books.append(book_name)
    return sorted(books)

# Function to generate book prompt using AutoGen
def generate_book_prompt(book_name, book_description):
    # Set up AutoGen configuration
    config = {
        "seed": 42,
        "temperature": 0.7,
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={"model": ["gpt-4"]}
        ),
    }
    
    # Create the assistant agent
    assistant = autogen.AssistantAgent(
        name="BookAnalysisAssistant",
        system_message="You are a helpful assistant for book analysis.",
        llm_config=config,
    )
    
    # Create the user proxy agent
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0
    )
    
    # Generate the book prompt template
    prompt_template = """
    # 书名
    {book_name}

    # 大致剧情：
    请根据以下书籍描述，创建一个生动、详细的剧情概述，包括主要情节、人物分析和主题探讨：

    {book_description}

    请以markdown格式输出，确保内容丰富但不超过500字。
    """
    
    prompt = prompt_template.format(
        book_name=book_name,
        book_description=book_description
    )
    
    # Initiate the conversation to generate book prompt
    user_proxy.initiate_chat(
        assistant,
        message=prompt
    )
    
    # Get the response and save to file
    generated_content = assistant.last_message()["content"]
    
    # Save to file
    book_file_path = BOOK_PROMPT_DIR / f"{book_name}.md"
    with open(book_file_path, "w", encoding="utf-8") as f:
        f.write(generated_content)
    
    return generated_content

# UI Layout
st.title("📚 DeepReader Bookshelf")

# Sidebar for book management
with st.sidebar:
    st.header("Book Management")
    add_new_book = st.button("📖 Add New Book")

# Main area
tabs = st.tabs(["Book Library", "Add Book"])

# Book Library Tab
with tabs[0]:
    st.header("Book Library")
    
    # Display existing books
    existing_books = load_existing_books()
    
    if existing_books:
        book_columns = st.columns(3)
        
        for i, book_name in enumerate(existing_books):
            with book_columns[i % 3]:
                book_path = BOOK_PROMPT_DIR / f"{book_name}.md"
                
                with open(book_path, "r", encoding="utf-8") as f:
                    book_content = f.read()
                
                # Create a card for each book
                with st.container(border=True):
                    st.subheader(book_name)
                    
                    # Show a preview of the book content
                    preview = book_content.split("\n\n")[0:2]
                    st.write("\n\n".join(preview) + "...")
                    
                    # Add a button to view the full content
                    if st.button("View Details", key=f"view_{book_name}"):
                        st.session_state.selected_book = book_name
                        st.rerun()
    else:
        st.info("No books in the library yet. Add a new book to get started!")

# Add Book Tab
with tabs[1]:
    st.header("Add a New Book")
    
    book_name = st.text_input("Book Title")
    book_description = st.text_area("Book Description", height=200, 
                                   placeholder="Enter a brief description of the book, including its plot, themes, and main characters.")
    
    submitted = st.button("Generate and Save Book Prompt")
    
    if submitted and book_name and book_description:
        with st.spinner("Generating book prompt..."):
            try:
                # Generate the book prompt
                generated_content = generate_book_prompt(book_name, book_description)
                
                # Show success message
                st.success(f"Book '{book_name}' has been added to the library!")
                
                # Display the generated content
                st.subheader("Generated Book Prompt:")
                st.markdown(generated_content)
                
                # Refresh the book list
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error generating book prompt: {str(e)}")
    
    elif submitted:
        st.warning("Please fill in both the book title and description.")

# View book details if selected
if hasattr(st.session_state, 'selected_book'):
    book_name = st.session_state.selected_book
    book_path = BOOK_PROMPT_DIR / f"{book_name}.md"
    
    with open(book_path, "r", encoding="utf-8") as f:
        book_content = f.read()
    
    with st.expander("Book Details", expanded=True):
        st.markdown(book_content)
    
    # Clear selection if button clicked
    if st.button("Close Details"):
        del st.session_state.selected_book
        st.rerun()

# Footer
st.markdown("---")
st.caption("DeepReader Bookshelf - Add and manage books for your reader sessions")
