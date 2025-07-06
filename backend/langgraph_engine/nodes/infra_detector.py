# backend/langgraph_engine/nodes/infra_detector.py

from backend.services.infra_scanner import generate_infra_dependencies  # your regex/prompt logic

def detect_infra_dependencies(state):
    """
    Extract infra dependencies like databases, Redis, MQs from raw repo files.
    """
    repo_data = state.get("repos", {})  # dict[str, list[str]]  e.g. {"e-commerce": ["code1", "code2"]}
    
    infra_results = []
    for service, files in repo_data.items():
        for content in files:
            matches = generate_infra_dependencies(content)  # list of {"type": ..., "detail": ...}
            for m in matches:
                m["source"] = service
                infra_results.append(m)

    state["infra_dependencies"] = infra_results
    return state
