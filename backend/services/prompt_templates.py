import json
def get_call_extraction_prompt(code: str) -> str:
    return f"""
You are a code analyzer that extracts **outbound service calls** from source code.

Your job is to identify service-to-service communication patterns. The types of communication include:

- HTTP calls (e.g., `requests.get(url)`, `axios.post(url)`)
- Kafka producers (e.g., `producer.send(topic, data)`)
- gRPC client invocations (e.g., `stub.MyMethod(request)`)
- RabbitMQ publishing (e.g., `channel.basic_publish(...)`)
- Database calls (e.g., `cursor.execute("SELECT ...")`, `engine.execute(...)`, JDBC queries)

---

### Output Format:
Respond only in **JSON array** format as shown below:

```json
[
  {{
    "type": "http" | "kafka" | "grpc" | "RabbitMQ" | "database",
    "target": "<destination, topic, service name, URL, or database name>",
    "details": "<method, endpoint, topic name, or SQL query>"
  }}
]

CODE:
{code}
"""

import json

def get_inferencing_prompt(from_service: str, call_data: dict, available_services: list) -> str:
    return f"""
You are analyzing microservice connections.

## Goal:
Given a single outbound call made by the service `{from_service}`, your task is to **identify which known service** (from the list) it is calling.

## KNOWN SERVICES:
{', '.join(available_services)}

## OUTBOUND CALL DATA:
{json.dumps(call_data, indent=2)}

## Instructions:
- Use `target_guess` and `via` to infer the destination service.
- Match to one of the known services above.
- Do NOT guess a service not in the list.
- NEVER set the `to` field to `{from_service}` (the source itself).
- Set the `type` as provided.
- Set `via` as-is from input.

## Respond strictly in this JSON format:
[
  {{
    "from": "{from_service}",
    "to": "<matched service from the list above>",
    "type": "{call_data.get('type')}",
    "via": "{call_data.get('via')}"
  }}
]
"""
