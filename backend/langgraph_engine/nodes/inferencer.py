from backend.services.prompt_templates import get_inferencing_prompt
from backend.langgraph_engine.config import get_chat_client
from backend.services.scoring import compute_confidence
import json

llm = get_chat_client()

def match_services(state):
    calls = state.get("calls", [])  # list of dicts with file/class/method/type/target/via/source
    known_services = list(state.get("repos", {}).keys())
    print(f"[DEBUG] Total calls extracted = {len(calls)}")

    inferred_connections = []

    for call in calls:
        from_service = call["source"]
        print(f"[DEBUG] Matching for: {from_service} → via {call.get('target')}")

        prompt = get_inferencing_prompt(
            from_service=from_service,
            call_data=call,
            available_services=known_services
        )

        result = llm.invoke(prompt)
        print(f"[LLM Output] {from_service}:\n{result.content}")

        try:
            matches = json.loads(result.content)
            for m in matches:
                m["confidence"] = compute_confidence(
                    m["from"], m["to"], m.get("via", ""), known_services
                )
                inferred_connections.append(m)
        except json.JSONDecodeError:
            print(f"[WARN] Failed to parse JSON for {from_service} call: {call}")

    state["inferred"] = inferred_connections
    return state
