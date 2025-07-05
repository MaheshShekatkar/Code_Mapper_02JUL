# backend/langgraph_engine/parsers/treesitter_loader.py

from tree_sitter import Language
import os

LIB_PATH = os.path.join(os.path.dirname(__file__), "build", "my-languages.so")

def build_library():
    if not os.path.exists(LIB_PATH):
        os.makedirs(os.path.dirname(LIB_PATH), exist_ok=True)
        Language.build_library(
            LIB_PATH,
            [
                os.path.join(os.path.dirname(__file__), 'tree-sitter-java'),
                os.path.join(os.path.dirname(__file__), 'tree-sitter-c-sharp'),
            ]
        )

def load_languages():
    build_library()
    JAVA_LANGUAGE = Language(LIB_PATH, 'java')
    CSHARP_LANGUAGE = Language(LIB_PATH, 'c_sharp')
    return JAVA_LANGUAGE, CSHARP_LANGUAGE
