import json
import logging
from typing import List, Set, TypedDict, Tuple

import chromadb
import numpy as np
from chromadb import Settings, QueryResult, Metadata

from code_embedder import CodeEmbedder
from src.code_parser import Artifact

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
                'documentSize': len(document)
            }
            matches.append(match)

    return matches


class CodeSearcher:
    def __init__(self, collection_name: str, embedder: CodeEmbedder):
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedder = embedder
        logger.info(f"CodeSearcher initialized with collection: {collection_name}")

    def add_code_files(self, file_paths: List[str]):

        def process_file(path: str) -> Tuple[str, List[Artifact]]:
            try:
                artifacts = self.embedder.get_intelligent_file_embeddings(path)
                return path, artifacts
            except Exception as e:
                logger.error(f"Error processing file {path}: {str(e)}")
                raise

        documents: List[str] = []
        embeddings: List[np.ndarray] = []
        ids: Set[str] = set()
        metadatas: List[Metadata] = []

        for path in file_paths:
            try:
                path, artifacts = process_file(path)
                for artifact in artifacts:
                    id = f"{path}:{artifact.class_full_name}"
                    while id in ids:
                        id = f"{path}:{artifact.class_full_name}.{np.random.randint(0, 1000)}"
                    ids.add(id)
                    documents.append(artifact.content)
                    embeddings.append(artifact.embedding)
                    metadatas.append(Metadata(
                        path=path,
                        class_full_name=artifact.class_full_name,
                        start_line=artifact.start_line,
                        end_line=artifact.end_line
                    ))
            except Exception as e:
                logger.error(f"Error processing file {path}: {str(e)}")

        if documents and embeddings and ids:
            self.collection.add(documents=documents, embeddings=embeddings, ids=list(ids), metadatas=metadatas)
            logger.info(f"Added {len(documents)} documents to the collection.")
        else:
            logger.warning("No documents were added to the collection.")

    def search_code(self, query: str, n_results: int = 5) -> List[VectorMatch]:
        query = query.strip()
        # here may be a request to an LLM that adapts the query for better search in embeddings
        query_embeddings = self.embedder.get_query_embeddings(query)
        try:
            results = self.collection.query(query_embeddings=query_embeddings, n_results=n_results,
                                            include=['embeddings', 'documents', 'distances', 'metadatas'])
            logger.info(f"Search for '{query}' returned {len(results)} results")
            # here may be a request to a fast LLM (Groq for example) for better filtering and relevance scoring of the result
            print(json.dumps(results))
            return query_result_to_matches(results)
        except Exception as e:
            logger.error(f"Error during code search with query '{query}': {str(e)}")
            raise


    # def add_code_files_parallel(self, file_paths: List[str], max_workers: int = None):
    #     """
    #     Adds code files to the collection in parallel using a ThreadPoolExecutor.

    #     This method reads the contents of each file, generates embeddings for them using the provided embedder,
    #     and adds them to the collection. It does this in parallel, controlled by the max_workers parameter.

    #     Parameters:
    #     - file_paths (List[str]): A list of file paths to add to the collection.
    #     - max_workers (int, optional): The maximum number of threads to use for parallel execution. Defaults to None,
    #         which lets ThreadPoolExecutor decide.
    #     """

    #     def process_file(path: str) -> Tuple[str, List[Artifact]]:
    #         try:
    #             artifacts = self.embedder.get_intelligent_file_embeddings(path)
    #             return path, artifacts
    #         except Exception as e:
    #             logger.error(f"Error processing file {path}: {str(e)}")
    #             raise

    #     documents: List[str] = []
    #     embeddings: List[np.ndarray] = []
    #     ids: Set[str] = set()
    #     metadatas: List[Metadata] = []

    #     with ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         future_to_path = {executor.submit(process_file, path): path for path in file_paths}
    #         for future in as_completed(future_to_path):
    #             path = future_to_path[future]
    #             try:
    #                 path, artifacts = future.result()
    #                 for artifact in artifacts:
    #                     # if ids contains the same id, just add rnd number to it
    #                     id = f"{path}:{artifact.class_full_name}"
    #                     while id in ids:
    #                         id = f"{path}:{artifact.class_full_name}.{np.random.randint(0, 1000)}"
    #                     ids.add(id)
    #                     documents.append(artifact.content)
    #                     embeddings.append(artifact.embedding)
    #                     metadatas.append(Metadata(
    #                         path=path,
    #                         class_full_name=artifact.class_full_name,
    #                         start_line=artifact.start_line,
    #                         end_line=artifact.end_line
    #                     ))
    #             except Exception as e:
    #                 logger.error(f"Error processing file {path}: {str(e)}")

    #     if documents and embeddings and ids:
    #         self.collection.add(documents=documents, embeddings=embeddings, ids=list(ids), metadatas=metadatas)
    #         logger.info(f"Added {len(documents)} documents to the collection.")
    #     else:
    #         logger.warning("No documents were added to the collection.")