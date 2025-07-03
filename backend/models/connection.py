from typing import TypedDict, List, Dict

class GraphState(TypedDict):
    repos: List[Dict]             # raw code files by repo
    calls: List[Dict]             # detected API/gRPC/kafka calls
    inferred: List[Dict]          # LLM-enhanced insights
    graph_data: Dict              # final graph structure
    graph_json: Dict
    connections: List[Dict]
    drift_report: Dict
