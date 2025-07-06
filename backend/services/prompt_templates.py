import json
import json

def get_call_extraction_prompt(files: dict) -> str:
    langauge= "Java"
    formatted_blocks = "\n\n".join(
        f"""### SERVICE: {service}
{code}""" 
        for service, code_list in files.items()
        for code in code_list
    )

    return f"""
You are analyzing outbound and inbound service calls made by the microservice.

## Follow these strict rules:
- Service is in {langauge} language
- For each file, extract any **inbound call** and **outbound call** made to other services.
- Always include `class`, `method`, and `type`.
- Always include message queue name/endpoint/method name in the `details` attribute.
- Do NOT include any markdown formatting like triple backticks or "json".
- No extra commentary or explanation.
- Output must be a valid JSON array.
- All outputs must follow the exact format shown below.

## Supported types:
- "http": HTTP/REST calls (e.g., HttpClient, RestTemplate, axios)
- "kafka": Kafka producer calls (e.g., producer.send)
- "grpc": gRPC client calls (e.g., stub.call)
- "rabbitmq": RabbitMQ calls (e.g., convertAndSend)
- "database": SQL/NoSQL DB access (JDBC, JPA, Hibernate, MongoTemplate)

## Output format:
[
  {{
    "class": "<class name>",
    "method": "<method name>",
    "type": "http" | "kafka" | "grpc" | "rabbitmq" | "database",
    "target": "<host, topic, or address>",
    "details": "<method or endpoint called>"
  }}
]

## Code to analyze:
{formatted_blocks}
"""

def get_inferencing_prompt(from_service: str, call_data: list, available_services: list) -> str:
    """
    from_service: name of the source microservice making the outbound call
    call_data: list of dicts with outbound call info (type, target_guess, class, method, etc.)
    available_services: list of known services to match against
    """
    
    return f"""
You are a code analysis expert helping to infer microservice dependencies.

## Goal:
Given a detailed outbound call made by the service `{from_service}`, identify which known service (from the list below) it is calling.

## Known Services:
{json.dumps(available_services, indent=2)}

## Outbound Call Data:
{json.dumps(call_data, indent=2)}

## Instructions:
- Match the `target_guess` or `via` field to the most appropriate service from the list of known services.
- Use available clues: service name, topic name, endpoint path, or naming similarity.
- If no confident match is possible, use `"unknown"` as the destination.
- Do **not** map a call to the same service (`{from_service}`).
- Output must include `from` in format: `<service>: <class>#<method>` for traceability.
- Do **not** include "json" or code fences in the output.
- Response must be valid JSON array and within 350 tokens.

## Output format (no markdown-style code fences):

[
  {{
    "from": "{from_service}: <class>#<method>",
    "to": "<best matching service from list above>",
    "type": "<http|grpc|kafka|rabbitmq>",
    "via": "<endpoint or topic>"
  }}
]
"""


def get_call_extraction_prompt_from_metadata(code: str, service_name: str) -> str:
    return f"""
You are analyzing Java or C# source code from the service `{service_name}`.

Your task is to extract **metadata** about the code structure.

## For each method, return:
- `class`: the class name
- `method`: the method name
- `code`: the method body or surrounding 8–12 lines

Only include methods that:
- Appear to contain outbound service calls (e.g., HTTP, Kafka, gRPC, RabbitMQ)
- Include keywords like: `HttpClient`, `RestTemplate`, `post`, `get`, `send`, `publish`, `exchange`, `stub`, etc.
- Do not add json keyword in the beginning of json output  

## Respond in JSON:
[
  {{
    "class": "<class name>",
    "method": "<method name>",
    "code": "<code snippet>"
  }},
  ...
]

## CODE:
{code}
"""

def get_infra_extraction_prompt(code_snippet: str) -> str:
    return f"""
You are analyzing a code/config file. Extract any **infrastructure dependencies** like:

- Databases (e.g., MySQL, PostgreSQL, MongoDB)
- Caches (e.g., Redis)
- Message brokers (e.g., Kafka, RabbitMQ)
- Cloud storage (e.g., S3, Azure Blob)

Return JSON like:
[
  {{
    "type": "infrastructure",
    "subtype": "database" | "cache" | "broker" | "cloud_service",
    "name": "<infra name>",
    "via": "<connection string or host>",
    "used_by": "<current service>"
  }}
]

Code:
{code_snippet}
"""

