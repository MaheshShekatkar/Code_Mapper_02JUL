from langgraph.graph import StateGraph
from backend.langgraph_engine.nodes.repo_scanner import scan
from backend.langgraph_engine.nodes.call_detector import detect_calls
from backend.langgraph_engine.nodes.inferencer import match_services
from backend.langgraph_engine.nodes.graph_builder import build_graph

from backend.models.connection import GraphState

def create_pipeline():
    builder = StateGraph(GraphState)

    # Define pipeline nodes
    builder.add_node("scan", scan)
    builder.add_node("detect", detect_calls)
    builder.add_node("infer", match_services)
    builder.add_node("build_graph", build_graph)

    # Connect them
    builder.set_entry_point("scan")
    builder.add_edge("scan", "detect")
    builder.add_edge("detect", "infer")
    builder.add_edge("infer", "build_graph")

    # Set the last node
    builder.set_finish_point("build_graph")

    # Compile and return LangGraph DAG
    return builder.compile()
