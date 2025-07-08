def check_security(calls, rules):
    violations = []
    for call in calls:
        if any(proto in call.get("via", "") for proto in rules["forbidden_protocols"]):
            violations.append({
                "from": call["from"],
                "to": call["to"],
                "type": call["type"],
                "via": call["via"],
                "violation": "Insecure protocol used"
            })
    return violations

def check_observability(metadata, rules):
    violations = []
    for item in metadata:
        if not any(k in item["code"] for k in rules["required_keywords"]):
            violations.append({
                "file": item["file"],
                "class": item["class"],
                "method": item["method"],
                "violation": "Missing observability (logs, metrics, trace)"
            })
    return violations

def check_nfr_alignment(state, nfr_rules):
    calls = state.get("inferred", [])
    metadata = state.get("metadata", [])

    return {
        "security": check_security(calls, nfr_rules["security"]),
        "observability": check_observability(metadata, nfr_rules["observability"]),
        # add more: testability, cost, etc.
    }

import os
import re
import json
from typing import Dict, List

RULES_PATH = "backend/config/nfr_rules.json"


def load_nfr_rules() -> Dict:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_code_for_rules(code: str, rules: Dict) -> Dict[str, List[str]]:
    violations = {}
    for category, rule in rules.items():
        matched = []
        for pattern in rule.get("patterns", []):
            if re.search(pattern["regex"], code, re.IGNORECASE):
                matched.append(pattern["description"])
        if matched:
            violations[category] = matched
    return violations


def check_nfr_alignment(state):
    """
    Scans the code files from all services and detects NFR alignment issues.
    """
    repos = state.get("repos", {})  # { service_name: { file_path: content } }
    rules = load_nfr_rules()
    report = {}

    for service, files in repos.items():
        service_violations = {}
        for file_path, content in files.items():
            violations = scan_code_for_rules(content, rules)
            if violations:
                service_violations[file_path] = violations

        if service_violations:
            report[service] = service_violations

    state["nfr_alignment_report"] = report
    return state
