import streamlit as st
import os
import io
import numpy as np
from utils_st import extract_text_from_pdf_bytes, extract_metadata_from_pdf_bytes, embed_pub

# App title
st.set_page_config(page_title="PubRAG 📚")

st.title("Step 1")
st.header("Generate your publication database")

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

    #st.download_button('Download CSV', text_contents, 'text/csv')

    # Query and display the data you inserted
    # pet_owners = conn.query('SELECT title, author, year, filepath FROM papers')
    # st.dataframe(pet_owners)
    # st.write("Done!")
