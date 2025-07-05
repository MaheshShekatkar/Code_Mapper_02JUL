from backend.services.prompt_templates import get_inferencing_prompt
from backend.langgraph_engine.config import get_chat_client
from backend.services.scoring import compute_confidence
import json

llm = get_chat_client()

import json
from backend.services.prompt_templates import get_inferencing_prompt
from backend.langgraph_engine.config import get_chat_client
from backend.services.scoring import compute_confidence

llm = get_chat_client()

def match_services(state):
    calls = state.get("calls", [])
    repo_map = state.get("repos", {})
    known_services = list(repo_map.keys())  # Only repo names

    inferred_connections = []

    for call in calls:
        source = call["source"]
        prompt = get_inferencing_prompt(
            from_service=source,
            call_data=call,  # includes type, target_guess, via
            available_services=known_services
        )

        try:
            result = llm.invoke(prompt)
            print(f"[match_services] LLM output for {source}: {result.content}")
            matches = json.loads(result.content)

            for m in matches:
                m["confidence"] = compute_confidence(
                    m["from"], m["to"], m.get("via", ""), known_services
                )
                inferred_connections.append(m)

        except json.JSONDecodeError:
            print(f"[match_services] Invalid JSON for {source}, skipping")
        except Exception as e:
            print(f"[match_services] Error processing {source}: {e}")

    state["inferred"] = inferred_connections
    return state
