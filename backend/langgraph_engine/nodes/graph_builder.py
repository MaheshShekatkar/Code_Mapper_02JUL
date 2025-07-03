import networkx as nx
import json

def build_graph(state):
    connections = state.get("graph_data", {})
    #print(connections)
    G = nx.DiGraph()

    # Add nodes and edges with attributes
    for conn in connections:
        from_svc = conn.get("from")
        to_svc = conn.get("to")
        call_type = conn.get("type")
        via = conn.get("via")

        G.add_node(from_svc, type="service")
        G.add_node(to_svc, type="service")
        G.add_edge(from_svc, to_svc, type=call_type, via=via)

    # Save the graph for downstream use
    state["graph_obj"] = G
    state["graph_json"] = nx.readwrite.json_graph.node_link_data(G)
    print(state["graph_json"] )
    return state
