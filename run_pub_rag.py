"""
    This script allows the user to pose a question about a publication in their directory of scientific 
    PDFs and return an answer from the desired paper, along with that paper's reference. 

    Code adapted from https://learnbybuilding.ai/tutorials/rag-from-scratch

    USAGE:
        $ python run_pub_rag.py [DATABASE] [INDEX FILE] [QUERY]
"""
import requests
import json
import sys
import re
import os
import time

import sqlite3
import numpy as np
import faiss

from utils import return_best_pub_id, extract_text_from_pdf,  elapsed_time


def validate_user_input(user_input) -> None:
    db_path, index_path, user_input = user_input
    if not db_path.endswith(".db"):
        raise ValueError("Database needs to end in '.db'\n")
    if not index_path.endswith(".index"):
        raise ValueError("Database needs to end in '.index'\n")
    return None


if __name__=="__main__":

    db_path = sys.argv[1]
    index_path = sys.argv[2]
    user_query = sys.argv[3]

    # Load database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Return best match
    start1 = time.time()
    best_pub_indices = return_best_pub_id(user_query, index_path)
    row_id = best_pub_indices[0] + 1
    end1 = time.time()

    # Extract text info from database and pub PDF
    start2 = time.time()
    cursor.execute(f'SELECT author, year, title, filepath FROM papers WHERE id={row_id}')
    info = cursor.fetchone()
    citation = (f"({info[0]} et al., {info[1]}: {info[2]})")
    filepath = info[3]
    pub_text = extract_text_from_pdf(filepath)
    end2 = time.time()

    # LLM prompt
    prompt = """
    You are a bot that answers scientific questions in simple terms from the citation given. You answer in very short sentences and do not include extra information.
    This is the best matched paper content: {pub_text}
    The user question is: {user_query}
    Formulate an answer to the user based on the best matched paper content and the user input. 
    End by inserting the following citation without reformatting {citation}'.
    """

    # Get response from LLM using API call
    start3 = time.time()
    full_response = []
    url = 'http://localhost:11434/api/generate'
    data = {
        "model": "llama3.1",
        "prompt": prompt.format(user_query=user_query, pub_text=pub_text, citation=citation)
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
    try:
        count = 0
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'response' in decoded_line.keys():
                    full_response.append(decoded_line['response'])
                else:
                    print(decoded_line['error'])
                    exit()
    finally:
        response.close()
    print('\n\n', ''.join(full_response))
    end3 = time.time()

    print("\n------------------------------------------------------------\n",
          f"Time to find best match: \t{elapsed_time(start1, end1)}\n",
          f"Time to PDF extraction: \t{elapsed_time(start2, end2)}\n",
          f"Time to model inference: \t{elapsed_time(start3, end3)}\n",
          "------------------------------------------------------------\n"
          )
    