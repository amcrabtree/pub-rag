import streamlit as st
import os
import pandas as pd
import numpy as np
import sqlite3
from utils_st import extract_text_from_pdf_bytes, extract_metadata_from_pdf_bytes, embed_pub


st.set_page_config(page_title="Database", page_icon="🗄️")
st.write("## 🗄️ Database")

st.write("#### Create a SQLlite database file")

uploaded_pdf_files = st.file_uploader("Upload all your target PDFs here.", 
                                      type='pdf', accept_multiple_files=True,
                                      )

if uploaded_pdf_files:
    # Make database
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
    c.execute('DELETE FROM papers;')

    with st.spinner("Making database..."):
        for uploaded_file in uploaded_pdf_files:
            filename = str(uploaded_file.name)
            print(f"\tAdding {os.path.basename(filename)} to database...")
            
            bytes_data = uploaded_file.read()
            metadata = extract_metadata_from_pdf_bytes(bytes_data)
            embeddings = embed_pub(bytes_data)
            embedding_blob = np.array(embeddings).tobytes()
            
            c.execute('''
            INSERT INTO papers (title, author, year, filepath, embedding) 
            VALUES (?, ?, ?, ?, ?)
            ''', 
            (metadata['title'], metadata['author'], metadata['year'], filename, embedding_blob))
    
    conn.commit()
    
    # Display the database
    if st.button("Display database"):
        st.write("Your database:")
        papers_sql = conn.execute('SELECT author, year, title FROM papers')
        rows = papers_sql.fetchall()
        df = pd.DataFrame(rows, columns=['Author', 'Year', 'Title'])
        st.dataframe(df, hide_index=True) 

    with st.sidebar:
        with open("test/papers_db.sqlite", "rb") as file:
            st.download_button(
                label="Download Database",
                data=file,
                file_name="research_papers.db",
                mime="application/octet-stream"
            )
    conn.close()
