import json
from backend.services.prompt_templates import get_call_extraction_prompt,get_call_extraction_prompt_from_metadata
from backend.langgraph_engine.config import get_chat_client

llm = get_chat_client()

def detect_calls(state):
    repo_data = state.get("repos", {})
    outbound_calls = []

    for repo_name, files in repo_data.items():
        merged_code = "\n".join(files.values())[:16000]

        # Step 1: Extract metadata (methods likely to make outbound calls)
        meta_prompt = get_call_extraction_prompt_from_metadata(merged_code, service_name=repo_name)
        meta_result = llm.invoke(meta_prompt)

        try:
            metadata = json.loads(meta_result.content)
        except Exception as e:
            print(f"[detect_calls] Metadata extraction failed for {repo_name}: {e}")
            continue

        if not metadata:
            continue

        # Step 2: Pass metadata in batch
        call_prompt = get_call_extraction_prompt(repo_name, metadata)
        call_result = llm.invoke(call_prompt)

        try:
            extracted = json.loads(call_result.content)
            for call in extracted:
                outbound_calls.append({
                    "source": repo_name,
                    "type": call["type"],
                    "target_guess": call["target"],
                    "via": call["details"],
                    "class": call["class"],
                    "method": call["method"]
                })
        except Exception as e:
            print(f"[detect_calls] Call parsing failed for {repo_name}: {e}")

    state["calls"] = outbound_calls
    return state
