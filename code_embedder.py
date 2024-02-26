import os
import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CodeEmbedder:
    def __init__(self, model_name: str, max_seq_length: int = 8192):
        # Don't forget to do: huggingface-cli login
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        self.max_seq_length = max_seq_length
        logger.info(f"Initialized CodeEmbedder with model {model_name} and max sequence length {max_seq_length}")

    def get_files(self, path: str, extensions: List[str]) -> List[str]:
        files = []
        for r, d, f in os.walk(path):
            for file in f:
                if file.endswith(tuple(extensions)):
                    files.append(os.path.join(r, file))
        logger.info(f"Found {len(files)} files in path {path}")
        return files

    def get_file_contents(self, path: str) -> str:
        """Reads the contents of a file and returns it as a string."""
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    def find_breakpoints(self, text: str) -> List[int]:
        """Identifies logical breakpoints in the code to split into chunks."""
        breakpoints = []
        current_length = 0
        lines = text.split('\n')
        for i, line in enumerate(lines):
            current_length += len(line) + 1  # +1 for the newline character
            if current_length >= self.max_seq_length or (
                    line.strip() == '' and current_length > self.max_seq_length // 2):
                breakpoints.append(i)
                current_length = 0
        logger.debug(f"Identified {len(breakpoints)} breakpoints in text")
        return breakpoints

    def split_into_chunks(self, text: str, breakpoints: List[int]) -> List[str]:
        """Splits the text into chunks based on the provided breakpoints."""
        chunks = []
        start = 0
        for end in breakpoints:
            chunk = "\n".join(text.split('\n')[start:end + 1])
            chunks.append(chunk)
            start = end + 1
        if start < len(text.split('\n')):
            chunks.append("\n".join(text.split('\n')[start:]))
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def get_intelligent_file_embeddings(self, path: str) -> np.ndarray:
        """Generates an embedding for the file at the given path, handling large files intelligently."""
        text = self.get_file_contents(path)
        breakpoints = self.find_breakpoints(text)
        chunks = self.split_into_chunks(text, breakpoints)
        embeddings = np.array([self.model.encode(chunk) for chunk in chunks])
        avg_embedding = np.mean(embeddings, axis=0)
        logger.info(f"Generated embedding for file {path}")
        return avg_embedding

    def get_query_embeddings(self, query: str) -> List[int]:
        """
        Generates embeddings for a given query string using the SentenceTransformer model.

        Parameters:
        - query (str): The query string for which to generate embeddings.

        Returns:
        - np.ndarray: The generated embeddings as a numpy array.
        """
        try:
            embeddings = self.model.encode(query)
            logger.info(f"Generated embeddings for query: {query}")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings for query '{query}': {str(e)}")
            raise
