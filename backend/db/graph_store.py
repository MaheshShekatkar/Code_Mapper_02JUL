import networkx as nx
from networkx.readwrite import json_graph
import os
import json

GRAPH_PATH = os.getenv("GRAPH_JSON_PATH")

graph_db = nx.DiGraph()

def clear_graph():
    global graph_db
    graph_db = nx.DiGraph()

def store_graph(connections: list):
    """
    Save connections into in-memory graph and optionally to disk
    """
    clear_graph()

    for conn in connections:
        src = conn["from"]
        dst = conn["to"]
        graph_db.add_node(src, type="service")
        graph_db.add_node(dst, type="service")
        graph_db.add_edge(src, dst, **{
            "type": conn["type"],
            "via": conn["via"],
            "confidence": conn.get("confidence", 1.0)
        })

    # Optional: persist to disk
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(json_graph.node_link_data(graph_db), f, indent=2)

def get_graph_json():
    return json_graph.node_link_data(graph_db)
