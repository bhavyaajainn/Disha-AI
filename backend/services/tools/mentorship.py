import json
import os
from langchain.tools import tool  # ✅ Import added before usage

@tool("mentorship_tool", return_direct=True)
def mentorship_tool(query: str = "") -> str:
    """
    Fetches a list of mentorship programs from a local JSON file and optionally filters them based on a query.
    """
    json_path = os.path.join(os.path.dirname(__file__), "../../data/mentorship_links.json")

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ Error loading mentorship data: {str(e)}"

    query_clean = query.strip().strip("'").strip('"')

    if not query_clean:
        return "\n\n".join([
            f"👩‍🏫 **{m['title']}**\n- {m['description']}\n- 🔗 [Visit]({m['url']})"
            for m in data
        ])

    filtered = [
        m for m in data
        if query_clean.lower() in m["title"].lower() or query_clean.lower() in m["description"].lower()
    ]

    if not filtered:
        return f"⚠️ No mentorship programs found for '{query_clean}'"

    return "\n\n".join([
        f"👩‍🏫 **{m['title']}**\n- {m['description']}\n- 🔗 [Visit]({m['url']})"
        for m in filtered
    ])
