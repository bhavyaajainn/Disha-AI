from supabase import create_client
import os

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

def fetch_chat_history(user_id: str, limit: int = 5):
    response = supabase.table("chat_history")\
        .select("prompt, response")\
        .eq("user_id", user_id)\
        .order("timestamp", desc=False)\
        .limit(limit)\
        .execute()
    return response.data

def save_chat(user_id: str, prompt: str, response: str):
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "prompt": prompt,
        "response": response
    }).execute()
