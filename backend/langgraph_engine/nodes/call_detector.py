import json
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()

import json
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()

def detect_calls(state):
    repo_data = state.get("repos", {})
    outbound_calls = []

    for repo_name, files in repo_data.items():
        for file_name, content in files.items():
            if not content.strip():
                continue  # skip empty files

            code_snippet = content[:16000]
            prompt = get_call_extraction_prompt(code_snippet)

            try:
                result = llm.invoke(prompt)
                extracted = json.loads(result.content)

                for item in extracted:
                    outbound_calls.append({
                        "source": f"{repo_name}:{file_name}",   # ⬅️ more precise origin
                        "type": item.get("type"),
                        "target_guess": item.get("target"),
                        "via": item.get("details")
                    })

            except Exception as e:
                print(f"[detect_calls] Failed parsing call for {repo_name}/{file_name}: {e}")

    state["calls"] = outbound_calls
    return state

