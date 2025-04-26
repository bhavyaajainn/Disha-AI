import json
import os
from langchain.tools import tool

@tool("community_tool", return_direct=True)
def community_tool(query: str = "") -> str:
    """
    This function searches for tech communities and networks based on the query.
    It retrieves data from a JSON file and filters the results by the query.
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

    # Add a clear header and make the links more prominent
    header = "🌐 **Tech Communities and Networks**\n\n"
    footer = "\n\n💡 Click on the links above to connect with these communities and expand your professional network."
    
    community_listings = [
        f"**{c['title']}**\n- {c['description']}\n- 🔗 **[JOIN COMMUNITY]({c['url']})** ← Click to connect"
        for c in data
    ]
    
    return header + "\n\n".join(community_listings) + footer