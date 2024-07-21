from pdfminer.high_level import extract_text
import sys
import re
import os

def extract_and_reformat(filename: str):
    """ Extracts text from PDF and reformats to cut out unnecessary text.
    """
    text = extract_text(input_pdf)
    text = text.split("References")[0]
    text = re.sub('(\n.{0,2}\n)', ' ', text)
    return text

input_pdf = sys.argv[1]
outdir = sys.argv[2]

text = extract_and_reformat(input_pdf)

outfile = input_pdf.split(".pdf")[0] + ".txt"
if len(outdir) > 0:
    outfile = os.path.join(outdir, os.path.basename(outfile))
with open(outfile, 'w') as f: 
    f.write(text)