import subprocess
import os
from pathlib import Path
import shutil

# Function to check if a command exists
def command_exists(cmd):
    return shutil.which(cmd) is not None

# Function to install Node.js and npm using Homebrew
def install_node():
    if not command_exists("brew"):
        print("Homebrew not found. Please install Homebrew.")
        exit(1)

    print("Node.js is not installed. Installing...")
    subprocess.check_call(["brew", "install", "node"])

# Function to install tree-sitter CLI
def install_tree_sitter_cli():
    print("tree-sitter CLI is not installed. Installing...")
    subprocess.check_call(["npm", "install", "-g", "tree-sitter-cli"])

# Check for Node.js and npm, install if not found
if not command_exists("node"):
    install_node()

# Check for tree-sitter CLI, install if not found
if not command_exists("tree-sitter"):
    install_tree_sitter_cli()

# all grammars are here: https://tree-sitter.github.io/tree-sitter/#parsers

# Define grammars and their repositories
top4_languages = {
    "python": "tree-sitter-python",
    "java": "tree-sitter-java",
    "c_sharp": "tree-sitter-c-sharp",
    "javascript": "tree-sitter-javascript",
}

top30_languages = {
    "bash": "tree-sitter-bash",
    "c": "tree-sitter-c",
    "cpp": "tree-sitter-cpp",
    "c_sharp": "tree-sitter-c-sharp",
    "css": "tree-sitter-css",
    "dart": "UserNobody14/tree-sitter-dart",
    "elixir": "tree-sitter-elixir",
    "elm": "tree-sitter-elm",
    "go": "tree-sitter-go",
    "html": "tree-sitter-html",
    "java": "tree-sitter-java",
    "javascript": "tree-sitter-javascript",
    "json": "tree-sitter-json",
    "kotlin": "oxisto/kotlintree",
    "lua": "tree-sitter-lua",
    "php": "tree-sitter-php",
    "python": "tree-sitter-python",
    "ruby": "tree-sitter-ruby",
    "rust": "tree-sitter-rust",
    "scala": "tree-sitter-scala",
    "swift": "tree-sitter-swift",
    "typescript": "tree-sitter-typescript",
    "vue": "tree-sitter-vue",
    "yaml": "tree-sitter-yaml",
    "zig": "tree-sitter-zig",
    "haskell": "tree-sitter-haskell",
    "ocaml": "tree-sitter-ocaml"
}

# TODO: the installation of grammars is not working, need to fix it. Also, it can be in parallel.
def install_grammars(mode):
    GRAMMAR_DIR = Path("grammars")
    GRAMMAR_DIR.mkdir(parents=True, exist_ok=True)

    languages = top4_languages if mode == "top4" else top30_languages

    for lang, repo_name in languages.items():
        grammar_path = GRAMMAR_DIR / f"tree-sitter-{lang}.so"
        if grammar_path.exists():
            print(f"Grammar for {lang} already exists. Skipping...")
            continue

        print(f"Processing {lang}")
        repo = f"https://github.com/{repo_name}.git" if "/" in repo_name else f"https://github.com/tree-sitter/{repo_name}.git"

        base_repo_name = Path(repo_name).stem
        base_repo_path = Path(base_repo_name)  # Convert string to Path object

        if base_repo_path.exists():
            print(f"Removing existing directory {base_repo_name}")
            shutil.rmtree(base_repo_name)

        try:
            if not base_repo_path.exists():
                subprocess.check_call(["git", "clone", repo])
            os.chdir(base_repo_name)
            subprocess.check_call(["tree-sitter", "generate"])
            subprocess.check_call(["gcc", "-o", "parsing.o", "-c", "src/parsing.c", "-Isrc"])
            scanner_files = list(Path("src").glob("scanner.c"))
            if scanner_files:
                subprocess.check_call(["gcc", "-o", "scanner.o", "-c", str(scanner_files[0]), "-Isrc"])
                subprocess.check_call(["gcc", "-shared", "-o", "parsing.so", "parsing.o", "scanner.o"])
            else:
                subprocess.check_call(["gcc", "-shared", "-o", "parsing.so", "parsing.o"])
            
            if not grammar_path.parent.exists():
                grammar_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move("parsing.so", grammar_path)
        except subprocess.CalledProcessError as e:
            with open("install_grammar_error_log.txt", "a") as log_file:
                log_file.write(f"Error installing grammar for {lang}: {e}\n")
        finally:
            os.chdir("..")
            shutil.rmtree(base_repo_name, ignore_errors=True)

    print(f"All grammars have been installed in {GRAMMAR_DIR}.")

# Example usage
mode = "top30"  # or "top4", dynamically set this based on your requirements
install_grammars(mode)
