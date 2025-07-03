import os
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAI

DEPLOYMENT_NAME = "o4-mini"
print(os.getenv("OPENAI_API_KEY"))

def get_chat_client() -> AzureChatOpenAI:
    return AzureChatOpenAI(
      api_key=os.getenv("OPENAI_API_KEY"),
      api_version="2025-01-01-preview",
      azure_endpoint ="https://digital-ai-assistance.openai.azure.com/",
      deployment_name = DEPLOYMENT_NAME,
      temperature= 1,
  )
    
def get_client() -> AzureOpenAI:
 return AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint ="https://digital-ai-assistance.openai.azure.com/",
    deployment_name = DEPLOYMENT_NAME,
 )
 
 
try:
    response = get_chat_client().invoke("Hello, are you connected?")
    print("✅ Connection successful:", response.content)
except Exception as e:
    print("❌ Connection failed:", e)