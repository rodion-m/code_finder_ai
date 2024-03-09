import unittest
from unittest.mock import patch

# Assuming the CodeParser class is saved in a file named code_parser.py
from src.code_parser import ParserFactory


class TestCodeParserJava(unittest.TestCase):
    def setUp(self):
        self.parser = ParserFactory.get_parser('java')
        self.sample_java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }

    public void sampleMethod() {
        // Sample method
    }
}
"""

    def test_extract_class_name(self):
        """Test extracting class names from Java code."""
        tree = self.parser.parser.parse(bytes(self.sample_java_code, "utf8"))
        class_node = next(node for node in tree.root_node.children if node.type == 'class_declaration')
        class_name = self.parser.extract_class_name(class_node)
        self.assertEqual(class_name, "HelloWorld")

    def test_load_language_java(self):
        """Test loading the Java language grammar."""
        self.assertIsNotNone(self.parser.parser.language)

    def test_find_breakpoints_java(self):
        """Test finding breakpoints in Java code."""
        breakpoints = self.parser.find_breakpoints(self.sample_java_code)
        self.assertEqual(len(breakpoints), 2)  # Expecting main and sampleMethod as breakpoints
        self.assertIn(('main', self.sample_java_code.splitlines()[2].strip()), [(b[1], b[2]) for b in breakpoints])
        self.assertIn(('sampleMethod', self.sample_java_code.splitlines()[6].strip()),
                      [(b[1], b[2]) for b in breakpoints])

    def test_split_into_chunks(self):
        """Test splitting Java code into chunks based on breakpoints."""
        breakpoints = self.parser.find_breakpoints(self.sample_java_code)
        chunks = self.parser.split_into_chunks(self.sample_java_code, breakpoints)
        self.assertEqual(len(chunks), 3)  # The class declaration, main method, and sampleMethod


    def test_grammar_file_not_found(self):
        """Test handling when the Java grammar file is not found."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.parser.load_language('java')


if __name__ == '__main__':
    unittest.main()
