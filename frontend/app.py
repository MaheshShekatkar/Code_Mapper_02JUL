import streamlit as st
import requests
from pyvis.network import Network
import json

st.set_page_config(layout="wide")
st.title("🔗 Application Dependency Insights")

st.info("Enter your repo list (local paths) to scan")

with st.form("repo_form"):
    default = """
[
  { "name": "piggymetrics", "path": "https://github.com/sqshq/piggymetrics.git" }
]
"""
    repo_input = st.text_area("Repository Config", default, height=200)
    submitted = st.form_submit_button("Run Analysis")

if submitted:
    try:
        repo_list = json.loads(repo_input)  # optionally use json.loads
        response = requests.post("http://127.0.0.1:8000/scan", json={"repos": repo_list})

        if response.ok:
            data = response.json()
            
            st.subheader("🧠 Inferred Graph")
            print(data)
            graph_json = data["graph"]
            net = Network(height="600px", width="100%", directed=True)

            for node in graph_json["nodes"]:
                net.add_node(node["id"], label=node["id"], title=node.get("type", "service"))

            for edge in graph_json["links"]:
                net.add_edge(edge["source"], edge["target"], title=f"{edge['type']} - {edge['via']}")

            net.save_graph("graph.html")
            with open("graph.html", "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=650, scrolling=True)

            st.subheader("⚠️ Drift Report")
            st.json(data["drift"])
        else:
            st.error("Scan failed: " + response.text)
    except Exception as e:
        st.error(f"Input error: {e}")

# graph TD
#     subgraph Services
#         UserService
#         OrderService
#         InventoryService
#     end

#     subgraph Infrastructure
#         PostgreSQL[(PostgreSQL DB)]
#         RabbitMQ[(RabbitMQ)]
#         Redis[(Redis Cache)]
#         PaymentAPI[(Payment API)]
#     end

#     UserService --> PostgreSQL
#     UserService --> Redis

#     OrderService --> PostgreSQL
#     OrderService --> RabbitMQ
#     OrderService --> PaymentAPI

#     InventoryService --> PostgreSQL
#     InventoryService --> RabbitMQ
#     InventoryService --> Redis