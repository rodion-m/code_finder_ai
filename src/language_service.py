from typing import List, Dict


# Language Service to handle language-specific logic
class LanguageService:
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        'python': 'tree-sitter-python',
        'java': 'tree-sitter-java',
        'c#': 'tree-sitter-c_sharp',
        'javascript': 'tree-sitter-javascript',
        'bash': 'tree-sitter-bash',
        'c': 'tree-sitter-c',
        'cpp': 'tree-sitter-cpp',
        'css': 'tree-sitter-css',
        'dart': 'tree-sitter-dart',
        'elixir': 'tree-sitter-elixir',
        'elm': 'tree-sitter-elm',
        'go': 'tree-sitter-go',
        'html': 'tree-sitter-html',
        'json': 'tree-sitter-json',
        'kotlin': 'tree-sitter-kotlin',
        'lua': 'tree-sitter-lua',
        'markdown': 'tree-sitter-markdown',
        'php': 'tree-sitter-php',
        'ruby': 'tree-sitter-ruby',
        'rust': 'tree-sitter-rust',
        'scala': 'tree-sitter-scala',
        'swift': 'tree-sitter-swift',
        'typescript': 'tree-sitter-typescript',
        'vue': 'tree-sitter-vue',
        'yaml': 'tree-sitter-yaml',
        'zig': 'tree-sitter-zig',
        'haskell': 'tree-sitter-haskell',
        'ocaml': 'tree-sitter-ocaml',
    }

    @classmethod
    def get_grammar_path(cls, language: str) -> str:
        language_key = language.lower()
        if language_key not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        return f"../grammars/{cls.SUPPORTED_LANGUAGES[language_key]}.so"

    @classmethod
    def get_supported_extensions(cls, language: str) -> List[str]:
        extensions_mapping: Dict[str, List[str]] = {
            'python': ['.py'],
            'java': ['.java'],
            'c#': ['.cs'],
            'javascript': ['.js'],
            'bash': ['.sh'],
            'c': ['.c'],
            'cpp': ['.cpp', '.cc', '.cxx', '.hpp'],
            'css': ['.css'],
            'dart': ['.dart'],
            'elixir': ['.ex', '.exs'],
            'elm': ['.elm'],
            'go': ['.go'],
            'html': ['.html', '.htm'],
            'json': ['.json'],
            'kotlin': ['.kt', '.kts'],
            'lua': ['.lua'],
            'markdown': ['.md'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'rust': ['.rs'],
            'scala': ['.scala'],
            'swift': ['.swift'],
            'typescript': ['.ts', '.tsx'],
            'vue': ['.vue'],
            'yaml': ['.yaml', '.yml'],
            'zig': ['.zig'],
            'haskell': ['.hs'],
            'ocaml': ['.ml', '.mli'],
        }
        if language.lower() not in extensions_mapping:
            raise ValueError(f"Unsupported language for extensions: {language}")
        return extensions_mapping[language.lower()]
