import streamlit as st
import pandas as pd
from datetime import datetime

def show_page2():
    st.title("深读笔记")
    
    # Initialize session state for notes if not exists
    if "notes" not in st.session_state:
        st.session_state.notes = []
    
    # Create columns for the layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Text input for new notes
        note_text = st.text_area("添加新笔记", height=150)
        if st.button("保存笔记"):
            if note_text:
                new_note = {
                    "text": note_text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": []
                }
                st.session_state.notes.append(new_note)
                st.success("笔记已保存！")
    
    with col2:
        # Display statistics or filters
        st.subheader("笔记统计")
        st.write(f"总笔记数: {len(st.session_state.notes)}")
    
    # Display all notes
    st.subheader("我的笔记")
    for i, note in enumerate(st.session_state.notes):
        with st.expander(f"笔记 {i+1} - {note['timestamp']}"):
            st.write(note['text'])
            # Add edit and delete buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("编辑", key=f"edit_{i}"):
                    # Add edit functionality
                    pass
            with col2:
                if st.button("删除", key=f"delete_{i}"):
                    st.session_state.notes.pop(i)
                    st.rerun()

if __name__ == "__main__":
    show_page2() 