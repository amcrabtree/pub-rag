"""
    Contains utils associated with streamlit.
"""
import io
import os
import streamlit as st
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2') # Load the SBERT model


def extract_text_from_pdf_bytes(bytes) -> str:
    """ Extracts PDF text content from PDF bytes.
    """
    with io.BytesIO(bytes) as file:
        reader = PdfReader(file)
        text = ""
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            text += page.extract_text()
        text = text.split("References")[0]
    return text



def extract_metadata_from_pdf_bytes(bytes) -> dict:
    """ Extracts PDF metadata relevant for paper citation.
    """
    with io.BytesIO(bytes) as file:
        reader = PdfReader(file)
        info = reader.metadata
        return {
            "title": info.title,
            "author": info.author,
            "year": str(info.creation_date)[:4]  
        }



def embed_pub_sbert(bytes) -> np.ndarray:
    """ Embed publication files (assuming text files) using SBERT
    """
    pub_text = extract_text_from_pdf_bytes(bytes)
    embeddings = SBERT_MODEL.encode([pub_text])
    return embeddings



@st.cache_resource
def load_pdf(pdf_name):
    """ Embed publication files (assuming text files) using SBERT
    """
    loaders = [PyPDFLoader(pdf_name)]
    index = VectorstoreIndexCreator(
        embedding = HuggingFaceEmbeddings(model_name='all-MiniLM-L12-v2'),
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    ).from_loaders(loaders)
    return index
