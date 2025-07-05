# backend/langgraph_engine/nodes/inferencer.py

import json
from backend.services.prompt_templates import get_inferencing_prompt
from backend.langgraph_engine.config import get_chat_client
from backend.services.scoring import compute_confidence

llm = get_chat_client()

def match_services(state):
    calls = state.get("calls", [])
    repos = list(state.get("repos", {}).keys())
    print(f"[DEBUG] calls = {calls}")

    inferred_connections = []

    for call in calls:
        source = call["source"]
        print(f"[DEBUG] from_service = {source}")

        prompt = get_inferencing_prompt(
            from_service=source,
            call_data=call,  # includes class, method, type, target_guess, via
            available_services=repos
        )

        result = llm.invoke(prompt)
        print(f"[match_services] LLM output for {source}: {result.content}")

        try:
            matches = json.loads(result.content)
            for m in matches:
                m["confidence"] = compute_confidence(
                    m["from"], m["to"], m.get("via", ""), repos
                )
                # Attach class/method context for visualization clarity
                m["source_class"] = call.get("class")
                m["source_method"] = call.get("method")
                m["source_file"] = call.get("file")
                inferred_connections.append(m)
        except json.JSONDecodeError:
            print(f"[match_services] Invalid JSON for {source}, skipping")

    state["inferred"] = inferred_connections
    state["graph_data"] = inferred_connections
    return state
