"""
    This script allows the user to pose a question about a publication in their directory of scientific 
    PDFs and return an answer from the desired paper, along with that paper's reference. 

    Code adapted from https://learnbybuilding.ai/tutorials/rag-from-scratch
"""

import requests
import json
import sys
import re
import os


def jaccard_similarity(query, document):
    query = query.lower().split(" ")
    document = document.lower().split(" ")
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection)/len(union)


def return_response(user_input: str, pub_path_list: list):
    similarities = []
    for pub_file in pub_path_list:
        with open(pub_file, "r") as file:
            pub_text = file.read().replace("\n", " ") 
            similarity = jaccard_similarity(user_input, pub_text)
            similarities.append(similarity)
    best_pub_file = pub_path_list[similarities.index(max(similarities))]
    with open(best_pub_file, "r") as file:
        best_pub_text = file.read().replace("\n", " ") 
        return best_pub_file, best_pub_text


def filename_to_citation(filename: str) -> str:
    """ Reformats filename into citation format. 
    """
    year, author = "", ""
    author = os.path.basename(filename).split(" ")[0]
    match = re.match(r'.*([0-9]{4}).*', filename)
    if match is not None: year = match.group(1)
    citation = f"({author} et al., {year})"
    return citation


if __name__=="__main__":

    user_input = sys.argv[1]
    pub_dir = "test/corpus"
    pub_path_list = [os.path.join(pub_dir, f) for f in os.listdir(pub_dir) if f.endswith(".txt")]

    best_pub_file, best_pub_text = return_response(user_input, pub_path_list)
    citation = filename_to_citation(best_pub_file)

    # LLM prompt
    prompt = """
    You are a bot that answers scientific questions in simple terms from the citation given. You answer in very short sentences and do not include extra information.
    This is the best matched paper content: {best_pub_text}
    The user question is: {user_input}
    Formulate an answer to the user based on the best matched paper content and the user input. 
    End by inserting the following citation without reformatting {citation}'.
    """

    # Get response from LLM using API call
    full_response = []
    url = 'http://localhost:11434/api/generate'
    data = {
        "model": "llama3",
        "prompt": prompt.format(user_input=user_input, best_pub_text=best_pub_text, citation=citation)
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
