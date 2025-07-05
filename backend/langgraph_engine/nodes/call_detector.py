import json
import ast
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()


def extract_code_context(file_content: str) -> list:
    """
    Extracts classes/methods and outbound call lines (e.g., HTTP/gRPC/Kafka) with context.
    Returns a list of dictionaries: [{class, method, code_snippet}, ...]
    """
    results = []
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = ast.get_source_segment(file_content, node).splitlines()
                if any("http" in line.lower() or "grpc" in line.lower() or "send" in line.lower() for line in lines):
                    class_name = None
                    parent = getattr(node, 'parent', None)
                    while parent:
                        if isinstance(parent, ast.ClassDef):
                            class_name = parent.name
                            break
                        parent = getattr(parent, 'parent', None)

                    results.append({
                        "class": class_name,
                        "method": node.name,
                        "code": "\n".join(lines[:20])  # limit context
                    })
    except Exception as e:
        print(f"[ERROR] AST parsing failed: {e}")
    return results


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
