from typing import List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class CodeEmbedder:
    def __init__(self, model_name: str, max_seq_length: int = 8192):
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        self.max_seq_length = max_seq_length

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
        return chunks

    def get_intelligent_file_embeddings(self, path: str) -> Optional[np.ndarray]:
        """Generates an embedding for the file at the given path, handling large files intelligently."""
        try:
            text = self.get_file_contents(path)
            breakpoints = self.find_breakpoints(text)
            chunks = self.split_into_chunks(text, breakpoints)
            embeddings = np.array([self.model.encode(chunk) for chunk in chunks])
            avg_embedding = np.mean(embeddings, axis=0)
            return avg_embedding
        except Exception as e:
            print(f"Error in generating an embedding for the contents of file {path}: {str(e)}")
            return None


# Example usage
model_name = "jinaai/jina-embeddings-v2-base-code"  # Replace with the actual model name you're using
embedder = CodeEmbedder(model_name)

# Assuming you have a list of file paths
file_paths = ["path/to/file1.py", "path/to/file2.py"]  # Replace with your actual file paths
embeddings = {}

for path in file_paths:
    embedding = embedder.get_intelligent_file_embeddings(path)
    if embedding is not None:
        embeddings[path] = embedding
