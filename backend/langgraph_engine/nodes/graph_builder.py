# backend/langgraph_engine/nodes/graph_builder.py

def build_graph(state):
    inferred = state.get("inferred", [])
    nodes = {}
    links = []

    for conn in inferred:
        source = conn["from"]
        target = conn["to"]

        # Add source node
        if source not in nodes:
            nodes[source] = {
                "id": source,
                "label": source,
                "type": "service"
            }

        # Add target node
        if target not in nodes:
            nodes[target] = {
                "id": target,
                "label": target,
                "type": "service"
            }

        # Add edge with metadata
        links.append({
            "source": source,
            "target": target,
            "label": conn.get("type", "unknown"),
            "via": conn.get("via", ""),
            "class": conn.get("source_class"),
            "method": conn.get("source_method"),
            "file": conn.get("source_file"),
            "confidence": conn.get("confidence", 0.0)
        })

    graph_json = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": list(nodes.values()),
        "links": links
    }

    state["graph_json"] = graph_json
    state["connections"] = inferred  # optional for UI use
    return state
