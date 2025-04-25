import json
import os
from langchain.tools import tool

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

    if query_clean:
        filtered = [
            m for m in data
            if query_clean.lower() in m["title"].lower() or query_clean.lower() in m["description"].lower()
        ]
        
        if not filtered:
            return f"⚠️ No mentorship programs found for '{query_clean}'"
        
        data = filtered

    # Add a clear header and make the links more prominent
    header = "👩‍🏫 **Mentorship Programs and Resources**\n\n"
    footer = "\n\n💡 Click on the links above to access these mentorship opportunities and accelerate your career growth."
    
    mentorship_listings = [
        f"**{m['title']}**\n- {m['description']}\n- 🔗 **[ACCESS PROGRAM]({m['url']})** ← Click to join"
        for m in data
    ]
    
    return header + "\n\n".join(mentorship_listings) + footer