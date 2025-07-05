import json
import ast
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.langgraph_engine.config import get_chat_client
from backend.langgraph_engine.tree_sitter_support.parser_factory import PARSER_MAP

llm = get_chat_client()

def extract_code_context(file_path: str, content: str) -> list:
    ext = os.path.splitext(file_path)[1].lower()
    parser_tuple = PARSER_MAP.get(ext)
    if not parser_tuple:
        return []  # Unsupported language

    parser, _ = parser_tuple
    tree = parser.parse(bytes(content, 'utf8'))
    root = tree.root_node
    contexts = []

    def traverse(node, current_class=None, current_method=None):
        # Class detection
        if node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                current_class = content[name_node.start_byte:name_node.end_byte]

        # Method detection
        if node.type in ('method_declaration', 'function_definition'):
            name_node = node.child_by_field_name('name')
            if name_node:
                current_method = content[name_node.start_byte:name_node.end_byte]

        # Method call detection
        if node.type == 'method_invocation' and current_method:
            snippet = content[node.start_byte:node.end_byte]
            if any(key in snippet.lower() for key in ['http', 'send', 'post', 'fetch', 'produce']):
                start_line = content.count('\n', 0, node.start_byte)
                lines = content.splitlines()
                block_start = max(0, start_line - 5)
                block = '\n'.join(lines[block_start:block_start + 10])
                contexts.append({
                    'file': file_path,
                    'class': current_class,
                    'method': current_method,
                    'code': block
                })

        for child in node.children:
            traverse(child, current_class, current_method)

    traverse(root)
    return contexts


def detect_calls(state):
    repo_data = state.get("repos", {})
    outbound_calls = []

    for repo_name, files in repo_data.items():
        context_blocks = []
        for file_path, content in files.items():
            extracted = extract_code_context(content)
            for block in extracted:
                block["file"] = file_path
                context_blocks.append(block)

        # Send all blocks from the repo as a batch prompt
        prompt = get_call_extraction_prompt(repo_name, context_blocks)
        result = llm.invoke(prompt)

        try:
            extracted = json.loads(result.content)
            for item in extracted:
                outbound_calls.append({
                    "source": repo_name,
                    "file": item.get("file"),
                    "class": item.get("class"),
                    "method": item.get("method"),
                    "type": item.get("type"),
                    "target_guess": item["target"],
                    "via": item["details"]
                })
        except Exception as e:
            print(f"[detect_calls] Error parsing LLM output for {repo_name}: {e}")

    state["calls"] = outbound_calls
    return state
