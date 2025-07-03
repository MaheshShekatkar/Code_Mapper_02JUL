from backend.services.repo_loader import load_repositories

DEFAULT_REPOS = [
    { "name": "order-service", "path": "./repos/order" },
    { "name": "payment-service", "path": "./repos/payment" }
]

def scan(state):
    repo_config = state.get("repos") or DEFAULT_REPOS
    #print("repo_config",repo_config)
    state["repos"] = load_repositories(repo_config)
    return state
