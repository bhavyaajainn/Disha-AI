import json
import os
from langchain.tools import tool

@tool("community_tool", return_direct=True)
def community_tool(query: str = "") -> str:
    """
    Returns a list of community platforms from a local JSON file.
    """
    json_path = os.path.join(os.path.dirname(__file__), "../../data/community_links.json")
    
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ Error loading community data: {str(e)}"

    query = query.strip()
    if query:
        data = [
            c for c in data
            if query.lower() in c["title"].lower() or query.lower() in c["description"].lower()
        ]

    if not data:
        return f"⚠️ No communities found for '{query}'"

    return "\n\n".join([
        f"🌐 **{c['title']}**\n- {c['description']}\n- 🔗 {c['url']}"
        for c in data
    ])
