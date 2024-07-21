from pdfminer.high_level import extract_text
import sys
import re
import os

input_pdf = sys.argv[1]
outdir = sys.argv[2]

text = extract_text(input_pdf)
text = text.split("References")[0]
text = re.sub('(\n.{0,2}\n)', ' ', text)

outfile = input_pdf.split(".pdf")[0] + ".txt"
if len(outdir) > 0:
    outfile = os.path.join(outdir, basename(outfile))
with open(outfile, 'w') as f: f.write(text)