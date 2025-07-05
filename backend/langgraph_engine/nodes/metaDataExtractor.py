import os
import re
from typing import Dict, List

SUPPORTED_EXTENSIONS = (".java", ".cs")

# Define regex patterns for Java and C# (lightweight and extensible)
HTTP_CALL_PATTERN = re.compile(r"\b(http|https)://[\w\.-]+")
KAFKA_PRODUCER_PATTERN = re.compile(r"producer\.send\(.*?\)")
GRPC_CALL_PATTERN = re.compile(r"new\s+.*Stub\(.*?\)")
RABBITMQ_PATTERN = re.compile(r"rabbitmq.*(send|publish|convert).*?\(")

CLASS_PATTERN = re.compile(r"class\s+(\w+)")
METHOD_PATTERN = re.compile(r"(public|private|protected)?\s+(\w+\s+)+(?P<method>\w+)\s*\(.*?\)")


def extract_metadata_from_file(file_path: str, content: str) -> List[Dict]:
    """
    Extracts service-level metadata from a single Java or C# file.
    """
    ext = os.path.splitext(file_path)[1]
    if ext not in SUPPORTED_EXTENSIONS:
        return []

    metadata = []

    class_name = None
    class_match = CLASS_PATTERN.search(content)
    if class_match:
        class_name = class_match.group(1)

    for method_match in METHOD_PATTERN.finditer(content):
        method_name = method_match.group("method")
        method_block_start = method_match.start()
        method_block_end = method_block_start + 1000  # Read 1000 chars from match start
        snippet = content[method_block_start:method_block_end]

        if HTTP_CALL_PATTERN.search(snippet):
            metadata.append({
                "type": "http",
                "class": class_name,
                "method": method_name,
                "details": HTTP_CALL_PATTERN.search(snippet).group()
            })
        elif KAFKA_PRODUCER_PATTERN.search(snippet):
            metadata.append({
                "type": "kafka",
                "class": class_name,
                "method": method_name,
                "details": "kafka-producer"
            })
        elif GRPC_CALL_PATTERN.search(snippet):
            metadata.append({
                "type": "grpc",
                "class": class_name,
                "method": method_name,
                "details": "grpc-client"
            })
        elif RABBITMQ_PATTERN.search(snippet):
            metadata.append({
                "type": "rabbitmq",
                "class": class_name,
                "method": method_name,
                "details": "rabbitmq-producer"
            })

    return metadata


def extract_repo_metadata(repo_files: Dict[str, str]) -> List[Dict]:
    """
    Given a dict of {filepath: content}, extract metadata from each file.
    Returns a flat list of metadata objects.
    """
    all_metadata = []
    for file_path, content in repo_files.items():
        try:
            items = extract_metadata_from_file(file_path, content)
            all_metadata.extend(items)
        except Exception as e:
            print(f"[WARN] Failed to parse {file_path}: {e}")
    return all_metadata
