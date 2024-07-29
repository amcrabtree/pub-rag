"""
    Contains all utilities functions used in repo. 
"""
import os
import sqlite3
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2') # Load the SBERT model


def extract_text_from_pdf(pdf_path) -> str:
    """ Extracts PDF text content.
    """
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            text += page.extract_text()
        text = text.split("References")[0]
    return text



def extract_metadata_from_pdf(pdf_path: str) -> dict:
    """ Extracts PDF metadata relevant for paper citation.
    """
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        info = reader.metadata
        return {
            "title": info.title,
            "author": info.author,
            "year": str(info.creation_date)[:4]  
        }
    


def embed_pub(pdf_path: str) -> np.ndarray:
    """ Embed publication files (assuming text files)
    """
    pub_text = extract_text_from_pdf(pdf_path)
    embeddings = SBERT_MODEL.encode([pub_text])
    return embeddings



def make_database(db_path: str, pub_list: list) -> None:
    """ Make SQLlite database. 
    """
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a table for storing metadata and embeddings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year TEXT,
        filepath TEXT,
        embedding BLOB
    )
    ''')

    # Insert metadata and embeddings into the table
    for pub_path in pub_list:
        print(f"\tAdding {os.path.basename(pub_path)} to database...")
        embeddings = embed_pub(pub_path)
        metadata = extract_metadata_from_pdf(pub_path)
        embedding_blob = np.array(embeddings).tobytes()
        cursor.execute('''
                    INSERT INTO papers (title, author, year, filepath, embedding) 
                       VALUES (?, ?, ?, ?, ?)
                    ''', 
                    (metadata['title'], metadata['author'], metadata['year'], 
                     pub_path, embedding_blob))
    conn.commit()
    return None



def make_index_file(db_path, index_path):
    """ Save a file of faiss index values created from vector embeddings.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Print number of rows in database
    cursor.execute('SELECT COUNT(author) FROM papers')
    print(f"\n\tNumber of papers in database: {cursor.fetchall()[0][0]}")

    # Retrieve embeddings from the database
    cursor.execute('SELECT embedding FROM papers')
    embeddings = [np.frombuffer(row[0], dtype=np.float32) for row in cursor.fetchall()]
    embeddings = np.array(embeddings)

    # Create a FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Save the index to a file
    faiss.write_index(index, index_path)
    conn.close()



def return_best_pub_id(user_input: str, index_path: str):
    """ Returns highest relevant publication and citation info.
    """
    # Load the FAISS index from the file
    index = faiss.read_index(index_path)

    # Perform a search
    query_embedding = SBERT_MODEL.encode([user_input])[0].reshape(1, -1)
    _, I = index.search(query_embedding, k=1)  # Return top k nearest neighbors
    row_index_list = I[0]
    return row_index_list 



def elapsed_time(start_time, end_time) -> str:
    """ Returns elapsed time since input start in minutes and seconds.
    """
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    output_text = f"{minutes} min {seconds} sec"
    return output_text
