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

