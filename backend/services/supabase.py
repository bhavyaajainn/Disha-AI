from supabase import create_client
import os
import re

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

def scrub_pii(text: str) -> str:
    # Email pattern
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
    
    # Phone number patterns (various formats)
    text = re.sub(r'\b\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE REDACTED]', text)
    
    # Social security / ID number patterns
    text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[ID REDACTED]', text)
    
    # URLs with potential user IDs
    text = re.sub(r'https?://[^\s/]+/(?:user|profile|account|u)/[a-zA-Z0-9_-]+', '[URL REDACTED]', text)
    
    # Physical addresses (simplified pattern)
    text = re.sub(r'\b\d+\s+[A-Za-z0-9\s,]+(?:Ave|St|Rd|Blvd|Ln|Dr|Way|Ct|Sq|Tr|Pkwy|Cir)\b', '[ADDRESS REDACTED]', text)
    
    # WhatsApp/Telegram number patterns
    text = re.sub(r'\b(?:whatsapp|telegram|signal|viber)(?:\s+at)?\s+[+]?\d[\d\s-]{7,}', '[CONTACT REDACTED]', text)
    
    # LinkedIn profile patterns
    text = re.sub(r'linkedin\.com/in/[a-zA-Z0-9_-]+', '[LINKEDIN REDACTED]', text)
    
    # Other social media handles
    text = re.sub(r'@\w{2,}', '[SOCIAL MEDIA HANDLE REDACTED]', text)
    
    return text

def fetch_chat_history(user_id: str, limit: int = 5):
    response = supabase.table("chat_history")\
        .select("prompt, response")\
        .eq("user_id", user_id)\
        .order("timestamp", desc=False)\
        .limit(limit)\
        .execute()
    return response.data

def save_chat(user_id: str, prompt: str, response: str):
    clean_prompt = scrub_pii(prompt)
    clean_response = scrub_pii(response)
    
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "prompt": clean_prompt,
        "response": clean_response
    }).execute()