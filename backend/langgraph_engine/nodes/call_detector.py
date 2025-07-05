# backend/langgraph_engine/nodes/call_detector.py

import json
from backend.services.prompt_templates import get_call_extraction_prompt
from backend.services.metadata_extractor import extract_metadata_from_repos
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()

def detect_calls(state):
    """
    Extract outbound calls from parsed metadata (not plain code blobs).
    """
    repo_data = state.get("repos", {})
    all_calls = []

    metadata_by_service = extract_metadata_from_repos(repo_data)

    for repo_name, entries in metadata_by_service.items():
        for entry in entries:
            prompt = get_call_extraction_prompt(entry["code"])
            result = llm.invoke(prompt)
            try:
                extracted = json.loads(result.content)
                for item in extracted:
                    all_calls.append({
                        "source": repo_name,
                        "class": entry.get("class"),
                        "method": entry.get("method"),
                        "type": item["type"],
                        "target_guess": item["target"],
                        "via": item["details"],
                        "file": entry["file"]
                    })
            except Exception as e:
                print(f"[detect_calls] Error parsing LLM output for {repo_name}: {e}")

    state["calls"] = all_calls
    return state
