import json
def get_call_extraction_prompt(service_name: str, blocks: list) -> str:
    """
    Builds a prompt to extract outbound service calls from structured code blocks.

    Each block contains:
    - file: path to the source file
    - class: class name (optional)
    - method: method name
    - code: code snippet
    """

    code_section = "\n\n".join([
        f"""### File: {block.get("file")}
Class: {block.get("class") or "None"}
Method: {block["method"]}

```python
{block["code"]}
```"""
        for block in blocks
    ])

    return f"""
You are analyzing microservice `{service_name}` to detect **outbound service calls**.

## Goal:
For each function below, identify if it contains a call to another service (HTTP, Kafka, gRPC, RabbitMQ, etc).

## Types of calls:
- HTTP: requests.post, axios, fetch, WebClient, RestTemplate, etc.
- Kafka: producer.send, kafkaTemplate.send
- gRPC: stub.callXYZ(), grpcChannel.invoke
- RabbitMQ: basicPublish, template.convertAndSend

## Respond in JSON format like and do not include json keyword in the beginning of the json:
[
  {{
    "file": "service.py",
    "class": "OrderHandler",
    "method": "submit_order",
    "type": "http" | "kafka" | "grpc" | "rabbitmq",
    "target": "<service or topic or host>",
    "details": "<endpoint or method or topic name>"
  }},
  ...
]

## Code Blocks:
{code_section}
"""

import json

def get_inferencing_prompt(from_service: str, call_data: dict, available_services: list) -> str:
    known_service_lines = "\n".join(
        f"- {service}: {', '.join(files[:5])}"  # show up to 5 files per service for brevity
        for service, files in available_services.items()
    )
    return f"""
    You are a code analysis expert helping to infer **microservice dependencies**.

    ## Goal:
    Given a detailed outbound call made by the service `{from_service}`, identify which known service (from the list below) is being called.

    ## KNOWN SERVICES AND FILES:
    {known_service_lines}

    ## Known Services:
    {json.dumps(known_service_lines, indent=2)}

    ## Call Metadata:
    - **Source Service**: {from_service}
    - **File**: {call_data.get("file", "unknown")}
    - **Class**: {call_data.get("class", "unknown")}
    - **Method**: {call_data.get("method", "unknown")}
    - **Call Type**: {call_data.get("type")}
    - **Target Guess**: {call_data.get("target")}
    - **Via (Topic/Endpoint)**: {call_data.get("via")}

    ## Instructions:
    - Match the `target_guess` or `via` to the correct known service.
    - Use service name, topic, endpoint path, or naming similarity.
    - If no match is clear, pick `"unknown"` as destination.
    - DO NOT map the call to the same service (`{from_service}`).
    - Output should include source class + method for better traceability.
    - Do not include json keyword in the beginning of the json output 

    ## Output format (JSON only):
    [
      {{
        "from": "{from_service}:{call_data.get('class')}#{call_data.get('method')}",
        "to": "<matched service from list above>",
        "type": "{call_data.get('type')}",
        "via": "{call_data.get('via')}"
      }}
    ]
    """
