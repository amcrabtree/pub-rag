import streamlit as st
import os
import pandas as pd
import numpy as np
import sqlite3
from utils_st import extract_text_from_pdf_bytes, extract_metadata_from_pdf_bytes, embed_pub


st.set_page_config(page_title="Config", page_icon="⚙️")
st.write("## ⚙️ Config")


st.write("#### Enter your Replicate API token")
replicate_api = st.text_input(
    'Enter [Replicate](https://replicate.com/account/api-tokens) API token:', 
    type='password')

st.write("#### Upload your publication database")
uploaded_db = st.file_uploader("Upload SQLite database", type=["sqlite", "db"])

with st.sidebar:
    if ('api' in st.session_state) or (replicate_api.startswith('r8_') and len(replicate_api)==40):
        st.success('API token', icon='✅')
        st.session_state.api = replicate_api
    else:
        st.warning('API token required', icon='⚠️')

    if uploaded_db or ('pub_db' in st.session_state):
        st.success('Pub database', icon='✅')
        st.session_state.pub_db = uploaded_db
    else:
        st.warning('Pub database required', icon='⚠️')

# Connect to the SQLite database
if uploaded_db:
    if st.button("Display database"):
        conn = sqlite3.connect('test/papers_db.sqlite')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year TEXT,
            filepath TEXT,
            embedding BLOB
        )
        ''')

        with open("test/papers_db.sqlite", "wb") as f:
            f.write(uploaded_db.getbuffer())
    
        st.write("Your database:")
        papers_sql = conn.execute('SELECT author, year, title FROM papers')
        rows = papers_sql.fetchall()
        df = pd.DataFrame(rows, columns=['Author', 'Year', 'Title'])
        st.dataframe(df, hide_index=True) 
    
        # Close the database connection
        conn.close()
    