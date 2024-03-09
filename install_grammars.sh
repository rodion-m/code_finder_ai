#!/opt/homebrew/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -eo pipefail

# Function to install Node.js and npm using Homebrew
install_node() {
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew."
        exit 1
    fi

    echo "Node.js is not installed. Installing..."
    brew install node
}

# Function to install tree-sitter CLI
install_tree_sitter_cli() {
    echo "tree-sitter CLI is not installed. Installing..."
    npm install -g tree-sitter-cli
}

# Check for Node.js and npm, install if not found
command -v node &> /dev/null || install_node

# Check for tree-sitter CLI, install if not found
command -v tree-sitter &> /dev/null || install_tree_sitter_cli

# all grammars are here: https://tree-sitter.github.io/tree-sitter/#parsers

# Define grammars and their repositories for top4
declare -A top4_languages=(
    ["python"]="tree-sitter-python"
    ["java"]="tree-sitter-java"
    ["c_sharp"]="tree-sitter-c-sharp"
    ["javascript"]="tree-sitter-javascript"
)

declare -A top30_languages=(
    ["bash"]="tree-sitter-bash"
    ["c"]="tree-sitter-c"
    ["cpp"]="tree-sitter-cpp"
    ["c_sharp"]="tree-sitter-c-sharp"
    ["css"]="tree-sitter-css"
    ["dart"]="UserNobody14/tree-sitter-dart"
    ["elixir"]="tree-sitter-elixir"
    ["elm"]="tree-sitter-elm"
    ["go"]="tree-sitter-go"
    ["html"]="tree-sitter-html"
    ["java"]="tree-sitter-java"
    ["javascript"]="tree-sitter-javascript"
    ["json"]="tree-sitter-json"
    ["kotlin"]="tree-sitter-kotlin"
    ["lua"]="tree-sitter-lua"
    ["markdown"]="tree-sitter-markdown"
    ["php"]="tree-sitter-php"
    ["python"]="tree-sitter-python"
    ["ruby"]="tree-sitter-ruby"
    ["rust"]="tree-sitter-rust"
    ["scala"]="tree-sitter-scala"
    ["swift"]="tree-sitter-swift"
    ["typescript"]="tree-sitter-typescript"
    ["vue"]="tree-sitter-vue"
    ["yaml"]="tree-sitter-yaml"
    ["zig"]="tree-sitter-zig"
    ["haskell"]="tree-sitter-haskell"
    ["ocaml"]="tree-sitter-ocaml"
)

# Mode selection based on command-line argument
mode=$1
if [ -z "$mode" ]; then
    mode="top30"
fi

echo "Installing grammars for $mode"

case "$mode" in
    top4) languages=("${!top4_languages[@]}") ;;
    top30) languages=("${!top30_languages[@]}") ;;
    *) echo "Invalid mode. Please specify 'top4' or 'top20' or 'top30'."; exit 1 ;;
esac

# Directory to store grammars
GRAMMAR_DIR="grammars"
mkdir -p "$GRAMMAR_DIR"

# Loop through selected languages and clone, build, and move grammars
for lang in "${languages[@]}"; do

    if [ -d "$GRAMMAR_DIR/$lang" ]; then
        echo "Grammar for $lang already exists. Skipping..."
        continue
    fi

    echo "Processing $lang"
    # Determine the correct array based on mode
    declare -n current_languages=${mode}_languages

    repo_name=${current_languages[$lang]}

    # Check if the repository name includes a forward slash, indicating a custom location
    if [[ "$repo_name" == *"/"* ]]; then
        repo="https://github.com/$repo_name.git"
    else
        repo="https://github.com/tree-sitter/$repo_name.git"
    fi
    
    # Extract the base name of the repository
    base_repo_name=$(basename "$repo_name" .git)

    echo "Cloning $repo"

    # Remove existing directory if it exists
    if [ -d "$base_repo_name" ]; then
        echo "Removing existing directory $base_repo_name"
        rm -rf "$base_repo_name"
    fi

    git clone "$repo"
    
    # Change directory to the cloned repository
    cd "$base_repo_name"

    tree-sitter generate
    gcc -o parser.o -c src/parser.c -Isrc
    scanner_files=$(find src -name scanner.c)
    if [ ! -z "$scanner_files" ]; then
        gcc -o scanner.o -c $scanner_files -Isrc
        gcc -shared -o parser.so parser.o scanner.o
    else
        gcc -shared -o parser.so parser.o
    fi
    mv parser.so "../$GRAMMAR_DIR/tree-sitter-${lang}.so"
    cd ..
    rm -rf "$base_repo_name" # Cleanup
done

echo "All grammars have been installed in $GRAMMAR_DIR."
