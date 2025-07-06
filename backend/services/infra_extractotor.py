import re
from typing import List, Dict

INFRA_PATTERNS = [
    # Databases
    (r"jdbc:(postgresql|mysql|sqlserver):\/\/([\w\.-]+):?(\d+)?", "database"),
    (r"mongodb:\/\/([\w\.-]+):?(\d+)?", "database"),
    (r'spring\.datasource\.url\s*=\s*["\']?(jdbc:[^"\']+)', "database"),
    (r"UseNpgsql\(([^)]+)\)", "database"),

    # Redis and Caches
    (r"redis:\/\/([\w\.-]+):?(\d+)?", "cache"),
    (r"spring\.redis\.host.*([\w\.-]+)", "cache"),

    # Kafka and Brokers
    (r"kafka\.bootstrap\.servers.*([\w\.-:]+)", "broker"),
    (r"producer\.send\(([^)]+)\)", "broker"),

    # S3, Cloud
    (r"s3\.amazonaws\.com", "cloud_service"),
    (r"https:\/\/[\w\.-]+\.blob\.core\.windows\.net", "cloud_service")
]

def detect_infra_dependencies(service_name: str, files: Dict[str, str]) -> List[Dict]:
    """
    Scan code/config for infra dependencies.
    Args:
        service_name: name of the repo/service
        files: dict of filename -> content

    Returns:
        List of inferred infra connections.
    """
    results = []
    for filename, content in files.items():
        for pattern, infra_type in INFRA_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                target = match if isinstance(match, str) else ":".join([str(m) for m in match if m])
                results.append({
                    "from": service_name,
                    "to": target,
                    "type": "infrastructure",
                    "subtype": infra_type,
                    "via": filename
                })
    return results
