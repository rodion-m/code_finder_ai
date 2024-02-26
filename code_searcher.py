import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, TypedDict

import chromadb
from chromadb import Settings, QueryResult

from code_embedder import CodeEmbedder

logger = logging.getLogger(__name__)

chroma_client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(anonymized_telemetry=False))


class VectorMatch(TypedDict):
    id: str
    document: str
    """Than less distance, than more similar"""
    distance: float
    documentSize: int


def query_result_to_matches(query_result: QueryResult) -> List[VectorMatch]:
    """
    Converts a QueryResult to a list of matches, where each match is represented
    as a Match TypedDict with 'id', 'document', 'distance', and 'documentSize' keys.

    Args:
    - query_result (QueryResult): The query result to convert.

    Returns:
    - List[Match]: A list of matches.
    """
    matches: List[VectorMatch] = []

    # Ensure the query_result has the necessary data.
    if not query_result.get('ids') or not query_result.get('documents') or not query_result.get('distances'):
        raise ValueError("QueryResult is missing required data (ids, documents, distances).")

    # Loop through the ids, documents, and distances to create matches.
    for ids, documents, distances in zip(query_result['ids'], query_result['documents'], query_result['distances']):
        for id, document, distance in zip(ids, documents, distances):
            match: VectorMatch = {
                'id': id,
                'document': document,
                'distance': distance,
                'documentSize': len(document)  # Calculate and include the document size
            }
            matches.append(match)

    return matches


class CodeSearcher:
    def __init__(self, collection_name: str, embedder: CodeEmbedder):
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedder = embedder
        logger.info(f"CodeSearcher initialized with collection: {collection_name}")

    # TODO: Move processors to different class implementations
    def add_code_files(self, file_paths: List[str], max_workers: int = None):
        """
        Adds code files to the collection in parallel using a ThreadPoolExecutor.

        This method reads the contents of each file, generates embeddings for them using the provided embedder,
        and adds them to the collection. It does this in parallel, controlled by the max_workers parameter.

        Parameters:
        - file_paths (List[str]): A list of file paths to add to the collection.
        - max_workers (int, optional): The maximum number of threads to use for parallel execution. Defaults to None,
            which lets ThreadPoolExecutor decide.
        """

        def process_file(path: str) -> Tuple[str, List[float], str]:
            try:
                content = self.embedder.get_file_contents(path)
                embedding = self.embedder.get_intelligent_file_embeddings(path)
                if embedding is not None:
                    return (content, embedding.tolist(), path)
                else:
                    logger.error(f"Failed to generate embedding for file: {path}")
                    return (None, None, None)
            except Exception as e:
                logger.error(f"Error processing file {path}: {str(e)}")
                raise

        documents = []
        embeddings = []
        ids = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {executor.submit(process_file, path): path for path in file_paths}
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    content, embedding, path = future.result()
                    if content is not None and embedding is not None:
                        documents.append(content)
                        embeddings.append(embedding)
                        ids.append(path)
                except Exception as e:
                    logger.error(f"Error processing file {path}: {str(e)}")

        if documents and embeddings and ids:
            self.collection.add(documents=documents, embeddings=embeddings, ids=ids)
            logger.info(f"Added {len(documents)} documents to the collection.")
        else:
            logger.warning("No documents were added to the collection.")

    def add_code_files_serial(self, file_paths: List[str]):
        documents = []
        embeddings = []
        ids = []

        for path in file_paths:
            try:
                content = self.embedder.get_file_contents(path)
                embedding = self.embedder.get_intelligent_file_embeddings(path)
                if embedding is not None:
                    documents.append(content)
                    embeddings.append(embedding.tolist())
                    ids.append(path)
                else:
                    logger.warning(f"Failed to generate embedding for file: {path}")
            except Exception as e:
                logger.error(f"Error processing file {path}: {str(e)}")
                continue

        if documents and embeddings and ids:
            self.collection.add(documents=documents, embeddings=embeddings, ids=ids)
            logger.info(f"Added {len(documents)} documents to the collection.")
        else:
            logger.warning("No documents were added to the collection.")

    def search_code(self, query: str, n_results: int = 5) -> List[VectorMatch]:
        query_embeddings = self.embedder.get_query_embeddings(query)
        try:
            results = self.collection.query(query_embeddings=query_embeddings, n_results=n_results,
                                            include=['embeddings', 'documents', 'distances'])
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return query_result_to_matches(results)
        except Exception as e:
            logger.error(f"Error during code search with query '{query}': {str(e)}")
            raise
