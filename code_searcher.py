import chromadb
from typing import Dict, Optional
import numpy as np

# Assuming a client setup for localhost, adjust according to your server setup
chroma_client = chromadb.HttpClient(host='localhost', port=8000)


class CodeSearcher:
    def __init__(self, collection_name: str):
        self.collection = chroma_client.get_or_create_collection(name=collection_name)

    def add_code_files(self, file_paths: List[str], embedder: CodeEmbedder):
        documents = []
        embeddings = []
        ids = []

        for path in file_paths:
            content = embedder.get_file_contents(path)
            embedding = embedder.get_intelligent_file_embeddings(path)
            if embedding is not None:
                documents.append(content)
                embeddings.append(embedding.tolist())
                ids.append(path)

        self.collection.add(documents=documents, embeddings=embeddings, ids=ids)

    def search_code(self, query: str, n_results: int = 5) -> List[str]:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return [result['document'] for result in results[0]['results']]

