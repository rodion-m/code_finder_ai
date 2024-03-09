import os
from typing import List
import numpy as np
from tree_sitter import Language, Parser

# Assuming LanguageService is implemented elsewhere correctly.
from language_service import LanguageService


class Artifact:
    def __init__(self, class_full_name: str, content: str, start_line: int, end_line: int,
                 embedding: np.ndarray = None):
        self.class_full_name = class_full_name
        self.content = content
        self.start_line = start_line
        self.end_line = end_line
        self.embedding = embedding

    def __repr__(self):
        return f"Artifact(class_full_name='{self.class_full_name}', content='{self.content}', start_line={self.start_line}, end_line={self.end_line})"


class CodeParser:
    def __init__(self, language: str):
        self.parser = Parser()
        self.language = language.strip().lower()
        self.load_language()

    def load_language(self):
        grammar_path = LanguageService.get_grammar_path(self.language)
        if not os.path.exists(grammar_path):
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}. You have to install it first.")
        self.parser.set_language(Language(grammar_path, self.language))

    def find_artifacts(self, text: str) -> List[Artifact]:
        tree = self.parser.parse(bytes(text, "utf8"))
        artifacts = []

        def traverse(node, parent_class_name=''):
            if node.type in ['function_definition', 'method_declaration']:
                artifact = self._create_artifact(node, text, parent_class_name)
                if artifact:
                    artifacts.append(artifact)

            for child in node.children:
                if child.type in ['class_declaration', 'class_definition']:
                    class_name = self.extract_class_name(child) or parent_class_name
                else:
                    class_name = parent_class_name
                traverse(child, class_name)

        traverse(tree.root_node)
        return artifacts

    def _create_artifact(self, node, text: str, parent_class_name: str) -> Artifact:
        start_row, end_row = node.start_point[0] + 1, node.end_point[0] + 1
        content = "\n".join(text.splitlines()[start_row - 1:end_row])
        class_name = parent_class_name
        return Artifact(class_full_name=class_name, content=content.strip(), start_line=start_row, end_line=end_row)

    def extract_class_name(self, node) -> str:
        # This might need adjustments based on the actual grammar definition of your programming language.
        class_name_node = next((n for n in node.children if n.type == 'type_identifier'), None)
        if class_name_node:
            return class_name_node.text.decode('utf8')
        return ""


class ParserFactory:
    @staticmethod
    def get_parser(language: str) -> CodeParser:
        return CodeParser(language)
