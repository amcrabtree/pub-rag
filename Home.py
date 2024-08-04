"""
    Homepage
"""
import streamlit as st

# Main title
st.set_page_config(page_title="PubRAG Home", page_icon="📚")
st.title("PubRAG 📚")

st.write(
    """
    **PubRAG uses your own collection of scientific articles to answer your niche questions and cite sources.**

    #### ⚙️ Config

    1. Enter your Replicate API token
     
    2. Create or upload your publication database

    #### 🔍 Query
    
    3. Run your query
    """)
