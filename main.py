import json
import logging
from typing import Union, Literal

from code_embedder import CodeEmbedder
from code_searcher import CodeSearcher

# Before running this script:
# 0. install cmake for onnx:
#   brew install cmake
# 1. run pip install -r requirements.txt
# 2. make sure to start the Chroma server:
#   docker run -d -p 8000:8000 --name chroma chromadb/chroma:latest
#   details: https://docs.trychroma.com/usage-guide#running-chroma-in-clientserver-mode
# 3. login to Hugging Face:
#   huggingface-cli login
#   details: https://huggingface.co/login


mode: Union[Literal["search"], Literal["index"]] = "search"
query_text = "azure code completion"

project_name = "codegpt"
project_path = "/Users/rodio/IdeaProjects/CodeGPT"
extensions = ['.java']

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

embedder = CodeEmbedder(model_name="jinaai/jina-embeddings-v2-base-code")
code_searcher = CodeSearcher(collection_name=project_name, embedder=embedder)

if mode == "index":
    # Index the codebase
    file_paths = embedder.get_files(project_path, extensions)
    code_searcher.add_code_files_serial(file_paths)
else:
    # Search the codebase
    search_results = code_searcher.search_code(query_text)
    print(json.dumps(search_results, indent=2))
