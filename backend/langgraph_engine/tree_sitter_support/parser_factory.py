# backend/langgraph_engine/tree_sitter_support/parser_factory.py
from tree_sitter import Language, Parser
import os

LANG_LIB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'my-languages.so')

JAVA = Language(LANG_LIB_PATH, 'java')
CSHARP = Language(LANG_LIB_PATH, 'c_sharp')

java_parser = Parser()
java_parser.set_language(JAVA)

csharp_parser = Parser()
csharp_parser.set_language(CSHARP)

# Export a central parser map
PARSER_MAP = {
    '.java': (java_parser, JAVA),
    '.cs': (csharp_parser, CSHARP)
}
