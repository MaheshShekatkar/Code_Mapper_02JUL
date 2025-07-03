import difflib

def compute_confidence(from_service: str, to_service: str, via: str, known_services: list) -> float:
    """
    Generic scoring for inferred service connections:
    - Similarity between 'via' and 'to_service'
    - Existence of 'to_service' in known services
    - Penalize self-call
    """

    score = 0.0

    # Normalize
    to_service_norm = to_service.lower().replace("-", "").replace("_", "")
    via_norm = via.lower().replace("-", "").replace("_", "")
    from_service_norm = from_service.lower().replace("-", "").replace("_", "")

    # 1. Does `via` include or resemble `to_service`?
    if to_service_norm in via_norm:
        score += 0.5
    else:
        # Use similarity metric as fallback
        similarity = difflib.SequenceMatcher(None, via_norm, to_service_norm).ratio()
        if similarity > 0.6:
            score += 0.4

    # 2. Is the target service a known service?
    known_normalized = [s.lower().replace("-", "").replace("_", "") for s in known_services]
    if to_service_norm in known_normalized:
        score += 0.3

    # 3. Penalize if it's a self-call
    if from_service_norm == to_service_norm:
        score -= 0.2

    # Final score between 0.0 and 1.0
    return round(min(max(score, 0.0), 1.0), 2)
