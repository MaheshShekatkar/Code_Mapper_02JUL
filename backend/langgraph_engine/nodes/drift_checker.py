def check_drift(state):
    actual = state.get("connections", [])
    expected = state.get("expected_connections", [])

    actual_set = {
        (conn["from"], conn["to"], conn["type"], conn["via"])
        for conn in actual
    }
    expected_set = {
        (conn["from"], conn["to"], conn["type"], conn["via"])
        for conn in expected
    }

    missing = expected_set - actual_set
    unexpected = actual_set - expected_set
    matched = actual_set & expected_set

    drift_report = {
        "missing": list(missing),
        "unexpected": list(unexpected),
        "matched": list(matched)
    }

    state["drift_report"] = drift_report
    return state
