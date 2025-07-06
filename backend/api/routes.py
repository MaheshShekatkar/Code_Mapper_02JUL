from fastapi import APIRouter, Request
from backend.langgraph_engine.build_graph import create_pipeline

router = APIRouter()
pipeline = create_pipeline()

@router.post("/scan")
async def run_dependency_scan(request: Request):
    body = await request.json()
    repos = body.get("repos", [])
    result = pipeline.invoke({ "repos": repos })
    print(result.get("graph_json"))
    return {
        "graph": result.get("graph_json"),
        "connections": result.get("connections"),
        "drift": result.get("drift_report"),
        "infra": result.get("infra_dependencies") 
    }

@router.get("/graph")
def get_saved_graph():
    graph = get_graph_json()
    return {
        "graph": graph
    }
    

@router.get("/details/{service_name}")
def get_service_details(service_name: str):
    if service_name not in graph_db:
        return {"error": "Service not found"}

    # Get outgoing calls
    outgoing = [
        {
            "to": tgt,
            **graph_db[service_name][tgt]
        }
        for tgt in graph_db.successors(service_name)
    ]

    # Get incoming calls
    incoming = [
        {
            "from": src,
            **graph_db[src][service_name]
        }
        for src in graph_db.predecessors(service_name)
    ]

    return {
        "service": service_name,
        "outgoing_calls": outgoing,
        "incoming_calls": incoming
    }
    
