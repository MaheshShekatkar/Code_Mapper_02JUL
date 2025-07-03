import json
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()

def detect_calls(state):
    repo_data = state.get("repos", {})
    outbound_calls = []

    for repo_name, files in repo_data.items():
        code_snippet = "\n".join(files)[:16000]
        prompt = get_call_extraction_prompt(code_snippet)
        result = llm.invoke(prompt)
        try:
            extracted = json.loads(result.content)
            for item in extracted:
                outbound_calls.append({
                    "source": repo_name,
                    "type": item["type"],
                    "target_guess": item["target"],
                    "via": item["details"]
                })
        except Exception as e:
            print(f"[detect_calls] Error parsing LLM output for {repo_name}: {e}")
    
    state["calls"] = outbound_calls
    return state
