# PubRAG

PubRAG is a RAG using your own folder of publication PDFs to help you answer questions and cite sources. This app was made because large language models (LLMs) like ChatGPT and others do not provide accurate citations for their responses and instead hallucinate them (i.e. they make up something random that sounds legit). The current version calculates a Jaccard similarity for finding the best match between the user prompt and the publication corpus, which takes longer than more modern techniques like using a vector database. This will likely be the next step in this project. Props to learnbybuilding.ai for providing a great [walkthrough](https://learnbybuilding.ai/tutorials/rag-from-scratch) and code to get me going. 


## Environment

PubRAG runs using ollama and some assorted Python libraries, including PDFMiner for scraping PDFs. Python 3.10 is used on Ubuntu OS CPU in this repo. 

```sh
pip install -r requirements.txt
curl -fsSL https://ollama.com/install.sh | sh
```

## Data

**Option 1:** Use your own folder of PDF files and save the path as the bash variable `PDF_DIR`.

**Option 2:** Download test data to a folder like the following (if using Ubuntu):

```sh
PDF_DIR="test/my_pdf_files"
mkdir -p $PDF_DIR test/corpus
wget https://www.nature.com/articles/s41467-023-44188-w.pdf -P $PDF_DIR
wget https://www.nature.com/articles/s41467-023-40066-7.pdf -P $PDF_DIR
```

Make sure to rename each file so that the Author name is the first word in the filename and there is a year present. This format enables citation parsing. For example: `Shaban 2023 - MAPS.txt`

```sh
mv $PDF_DIR/s41467-023-44188-w.pdf "$PDF_DIR/Shaban 2023 - MAPS.pdf"
mv $PDF_DIR/s41467-023-40066-7.pdf "$PDF_DIR/Amitay 2023 - CellSighter.pdf"
```


### Convert dataset to text files

Create a text file for each paper in corpus with `save_txt_file.py` script:

```sh
for pdf_file in ${PDF_DIR}/*.pdf; do
  echo Processing: $(basename "$pdf_file")
  python $MY_GIT_DIR/save_txt_file.py "$pdf_file" test/corpus
done
```


## Run PubRAG

### Pull the LLM using ollama

In order to use the LLM, you'll need to pull it from the web. 

```sh
ollama pull llama3
```

### Query

Now you can run the query script. Note that it pulls publication text from the `test/corpus` folder. 

```sh
python $MY_GIT_DIR/run_pub_rag.py \
  "What cell type accuracy did the CellSighter model achieve across all platforms?"
```


**A generated response from llama3 using PubRAG (took ~5 minutes for 2 papers on a CPU):**

&nbsp;&nbsp;*Unfortunately, the provided text does not explicitly mention the cell type accuracy of CellSighter model across all platforms. However, it describes several experiments and evaluations conducted to assess the performance of the CellSighter model.*

&nbsp;&nbsp;*One such evaluation is presented in Supplementary Fig. 3H-J, where the model was trained on two sets of labels (lineage classes "DCs" and "Macrophages", as well as subsets of these classes) and evaluated on a test set. This suggests that the cell type accuracy may vary depending on the specific classification task or platform used.*

&nbsp;&nbsp;*To provide more accurate information, I would recommend consulting the original research article or contacting the authors directly to inquire about the cell type accuracy achieved by the CellSighter model across all platforms.*

&nbsp;&nbsp;*(Amitay et al., 2023)*

> [!NOTE]
> Well, the Jaccard index did find the correct citation, but llama3 somehow missed the introduction that states the model's accuracy. Maybe it doesn't do well with interpreting numeric values.


Another query:

```sh
python $MY_GIT_DIR/run_pub_rag.py \
  "What does CellSighter do?"
```

**Output:**

&nbsp;&nbsp;*Based on the provided text, CellSighter is a model that classifies cells into different lineages or subsets using membrane protein signals. It takes into account various factors such as image resolution, normalization methods, and the presence of functional proteins to make accurate predictions.*

&nbsp;&nbsp;*To be more specific, CellSighter was trained on images of cell membranes with CD4 and CD20 signals removed to avoid any confounding effects. The model was then tested using different input sizes, normalization methods, and over-clustering techniques to improve its performance.*

&nbsp;&nbsp;*In summary, CellSighter is a computational tool that uses machine learning algorithms to classify cells into different lineages or subsets based on their membrane protein signals.*

&nbsp;&nbsp;*(Amitay et al., 2023)*


> [!NOTE]
> Actually, this result is surprisingly good. It pointed out details that I missed! Guess it does better at summarizing and describing. Though, the first time I tried this question, it said the model does cell segmentation, which I believe was incorrect. It generates a new response each time, so I'm not sure how much to trust it.



## TODO

- [ ] Create a vector db to encode pubs (decrease latency speed)
- [ ] Add more publications and clock latency time
- [ ] Compare latency times on GPU


* * *

## References

 - ["A beginner's guide to building a Retrieval Augmented Generation (RAG) application from scratch" by learnbybuilding.ai](https://learnbybuilding.ai/tutorials/rag-from-scratch)

