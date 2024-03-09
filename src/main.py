import os
import json
import logging
from typing import Union, Literal

from code_embedder import CodeEmbedder
from code_searcher import CodeSearcher
from code_parser import CodeParser
from src.language_service import LanguageService

# Before running this script:
# 0. install brew:
#   ...
# 0. install cmake for onnx:
#   brew install cmake
# 1. run pip install -r requirements.txt
# 2. make sure to start the Chroma server:
#   docker run -d -p 8000:8000 --name chroma chromadb/chroma:latest
#   details: https://docs.trychroma.com/usage-guide#running-chroma-in-clientserver-mode
# 3. login to Hugging Face:
#   huggingface-cli login
#   details: https://huggingface.co/login
# 4. Install  tree-sitter parsers:
# brew install bash
# chmod +x install_grammars.sh
# ./install_grammars.sh


mode: Union[Literal["search"], Literal["index"]] = "search"
query_text = "azure code completion"

project_name = "codegpt5"
project_path = "/Users/rodio/IdeaProjects/CodeGPT"
language = "java"

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# if dir grammars doesn't exist throw error
if not os.path.exists("../grammars"):
    raise Exception("Grammars directory not found. Please run `./install_grammars.sh` to install grammars.")

language_service = LanguageService()
embedder = CodeEmbedder(model_name="jinaai/jina-embeddings-v2-base-code", language=language,
                        language_service=language_service)
code_searcher = CodeSearcher(collection_name=project_name, embedder=embedder)

if mode == "index":
    # Index the codebase
    file_paths = embedder.get_files(project_path)
    code_searcher.add_code_files(file_paths)
    print("Indexing complete.")
else:
    # Search the codebase
    search_results = code_searcher.search_code(query_text)
    print(json.dumps(search_results, indent=2))
