import streamlit as st

def generate_dependency_report(state: dict) -> str:
    connections = state.get("inferred", [])
    drift = state.get("drift_report", {})
    mermaid = export_to_mermaid(connections)

    lines = []

    lines.append("# 📊 Microservice Dependency Report")
    lines.append("")

    # Mermaid Diagram
    lines.append("## 🔗 Dependency Graph (Mermaid)")
    lines.append("```mermaid")
    lines.append(mermaid)
    lines.append("```")
    lines.append("")

    # Connections Table
    lines.append("## 📌 Inferred Connections")
    lines.append("| From | To | Type | Via | Class | Method | Confidence |")
    lines.append("|------|----|------|-----|--------|--------|------------|")
    for edge in connections:
        lines.append(
            f"| {edge['from']} | {edge['to']} | {edge['type']} | {edge.get('via','')} | "
            f"{edge.get('class','')} | {edge.get('method','')} | {edge.get('confidence',''):.2f} |"
        )
    lines.append("")

    # Drift Report if available
    if drift:
        lines.append("## ⚠️ Drift Report")
        for issue in drift.get("issues", []):
            lines.append(f"- {issue}")

    # Exported Formats
    lines.append("## 🛠 Export Formats")
    lines.append("You can export this graph in:")
    lines.append("- Mermaid (above)")
    lines.append("- Graphviz DOT")
    lines.append("- Cypher for Neo4j")

    return "\n".join(lines)


def render_mermaid_graph(mermaid_code: str):
    st.markdown("## 🔗 Dependency Graph", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mermaid">
    {mermaid_code}
    </div>
    """, unsafe_allow_html=True)

    # This loads the Mermaid JS script for rendering
    st.components.v1.html("""
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true });
    </script>
    """, height=0)
    
 
def export_to_mermaid(connections: list) -> str:
    """
    Converts a list of service connections to a Mermaid diagram string.
    """
    lines = ["```mermaid", "graph TD"]

    for conn in connections:
        from_service = conn.get("from", "unknown")
        to_service = conn.get("to", "unknown")
        via = conn.get("via", "")
        conn_type = conn.get("type", "").upper()

        # Skip invalid or incomplete connections
        if from_service == to_service or to_service.lower() == "unknown":
            continue

        label = f"{conn_type}: {via}" if via else conn_type
        lines.append(f'    {from_service} -->|{label}| {to_service}')

    lines.append("```")
    return "\n".join(lines)
    
