import streamlit as st
import os
import io
import numpy as np
from utils_st import extract_text_from_pdf_bytes, extract_metadata_from_pdf_bytes, embed_pub


st.set_page_config(page_title="Config", page_icon="⚙️")
st.title('PubRAG Config 📚⚙️')

st.write("## ⚙️ Config")

st.write("#### Enter your Replicate API token")
if 'api' in st.session_state:
    st.success('API token provided', icon='✅')
else:
    st.session_state.api = st.text_input(
        'Enter [Replicate](https://replicate.com/account/api-tokens) API token:', 
        type='password')
    if not (st.session_state.api.startswith('r8_') and len(st.session_state.api)==40):
        st.warning('API token required', icon='⚠️')
    else:
        st.success('API token provided', icon='✅')
os.environ['REPLICATE_API_TOKEN'] = st.session_state.api

st.write("#### Create or upload your publication database")

uploaded_files = st.file_uploader("Upload all your target PDFs here.", 
                                  type='pdf', accept_multiple_files=True,
                                  )

if uploaded_files is not None:
    # Connect to SQLite database and insert data
    conn = st.connection('papers_db', type='sql')
    with conn.session as s:
        s.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year TEXT,
            filepath TEXT,
            embedding BLOB
        )
        ''')
        s.execute('DELETE FROM papers;')
        for uploaded_file in uploaded_files:
            filename = str(uploaded_file.name)
            print(f"\tAdding {os.path.basename(filename)} to database...")
            bytes_data = uploaded_file.read()
            embeddings = embed_pub(bytes_data)
            metadata = extract_metadata_from_pdf_bytes(bytes_data)
            #print(f"\n\nMETADATA: {embeddings}\n\n")
            embedding_blob = np.array(embeddings).tobytes()
            s.execute('''
                        INSERT INTO papers (title, author, year, embedding) 
                        VALUES (?, ?, ?, ?)
                        ''', 
                        (metadata['title'], metadata['author'], metadata['year'], 
                        embedding_blob))
        s.commit()

    
    # Query and display the data you inserted
    papers_db = conn.query('SELECT title, author, year, filepath FROM papers')
    st.dataframe(papers_db)
    st.write("Done!")

    st.download_button('Download CSV', text_contents, 'text/csv')


