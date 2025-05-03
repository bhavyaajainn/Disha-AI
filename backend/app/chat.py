from fastapi import APIRouter, Request
from services.supabase import fetch_chat_history, save_chat
from services.model_selector import select_model
from services.langchain.agent import ask_disha_with_tools
from services.bedrock import ask_bedrock
from services.bias_detector import is_gender_biased
from services.context_manager import EphemeralContextManager
from datetime import datetime
import hashlib
import time
import re

router = APIRouter()

FALLBACK_GUARDRAIL_RESPONSE = "Sorry, I can't help with that. Let's focus on career-related questions instead."
context_manager = EphemeralContextManager()

def is_career_related(text: str) -> bool:
    text_lower = text.lower().strip()

    if is_explicitly_non_career(text_lower):
        return False

    if contains_career_keywords_or_phrases(text_lower):
        return True

    if is_question_with_career_context(text_lower):
        return True

    if is_list_request_for_career_topics(text_lower):
        return True

    return False


def is_explicitly_non_career(text: str) -> bool:
    non_career_topics = get_non_career_topics()
    list_patterns = get_list_patterns()

    for pattern in list_patterns:
        if re.match(pattern, text) and not contains_career_terms(text):
            if any(topic in text for topic in non_career_topics):
                return True

    for topic in non_career_topics:
        if topic in text and len(text.split()) < 10:
            return True

    for topic_phrase in [f"tell me about {topic}" for topic in non_career_topics]:
        if topic_phrase in text:
            return True

    return False


def contains_career_keywords_or_phrases(text: str) -> bool:
    career_keywords = get_career_keywords()
    career_phrases = get_career_phrases()

    if any(keyword in text for keyword in career_keywords):
        return True

    if any(phrase in text for phrase in career_phrases):
        return True

    return False


def is_question_with_career_context(text: str) -> bool:
    question_starters = ["how", "what", "when", "where", "why", "who", "can"]
    non_career_topics = get_non_career_topics()

    if any(text.startswith(starter) for starter in question_starters):
        if any(f"{starter} {topic}" in text for starter in question_starters for topic in non_career_topics):
            return False
        return True

    return False


def is_list_request_for_career_topics(text: str) -> bool:
    if ("list" in text or "show" in text) and contains_career_terms(text):
        return True
    return False


def contains_career_terms(text: str) -> bool:
    career_terms = ["job", "career", "skill", "course", "training", "resume", "cv", "company", "opportunity"]
    return any(term in text for term in career_terms)


def get_non_career_topics() -> list:
    return [
        "movie", "film", "cinema", "imdb", "rating", "actor", "actress", "director", "box office",
        "song", "music", "album", "band", "singer", "concert", "lyrics", "playlist",
        "medicine", "medical", "health", "doctor", "anxiety", "depression", "therapy", "drug", "pill",
        "game", "play", "sport", "team", "athlete", "football", "basketball", "baseball",
        "recipe", "food", "cook", "restaurant", "celebrity", "politics", "news", "weather",
        "tv show", "book", "novel", "story", "poem", "religion", "god", "birthday", "wedding",
        "dating", "relationship", "breakup", "girlfriend", "boyfriend", "prayer", "worship",
        "travel", "vacation", "holiday", "flight", "tickets", "hotel", "tourism",
        "anime", "manga", "comic", "superhero", "marvel", "dc", "pet", "dog", "cat"
    ]


def get_list_patterns() -> list:
    return [
        r"list of .+",
        r"list .+ songs",
        r"list .+ movies",
        r"show me .+ list",
        r"give me list of .+",
        r"what are the .+ songs",
        r"top \d+ .+"
    ]


def get_career_keywords() -> list:
    return [
        "job", "career", "resume", "cv", "interview", "skill", "profession",
        "workplace", "salary", "hiring", "mentor", "education", "degree",
        "certification", "industry", "employment", "work", "company",
        "position", "role", "application", "promotion", "leadership",
        "professional", "business", "office", "team", "manager", "experience",
        "recruit", "talent", "hr", "human resources", "training", "development",
        "coaching", "remote", "hybrid", "office", "startup", "corporate",
        "tech", "technology", "software", "engineering", "developer", "design",
        "marketing", "finance", "project", "product", "data", "analyst",
        "portfolio", "network", "networking", "opportunity", "growth", "learn",
        "job search", "job market", "gap", "break", "returning", "workforce"
    ]


def get_career_phrases() -> list:
    return [
        "going back to work", "return to work", "change my career",
        "looking for a job", "find a job", "get hired", "get a job",
        "career change", "earn more", "switch careers", "career advice",
        "professional advice", "working parent", "working mother", "working father",
        "stay at home", "maternity leave", "paternity leave", "career break",
        "employment gap", "resume gap", "returning to workforce", "career transition"
    ]

def scrub_pii(text: str) -> str:
  
    # Email pattern
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
    
    # Phone number patterns (various formats)
    # Simplified phone number patterns
    phone_patterns = [
        r'\b\+\d{1,3}[\s-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # International format
        r'\b\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'  # Local format
    ]
    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE REDACTED]', text)
    
    # Social security / ID number patterns
    text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[ID REDACTED]', text)
    
    # URLs with potential user IDs
    text = re.sub(r'https?://[^\s/]+/(?:user|profile|account|u)/[a-zA-Z0-9_-]+', '[URL REDACTED]', text)
    
    # Physical addresses (simplified pattern)
    address_patterns = [
        r'\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd)\b',
        r'\b\d+\s+[A-Za-z0-9\s,]+(?:Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
        r'\b\d+\s+[A-Za-z0-9\s,]+(?:Way|Court|Ct|Plaza|Square|Sq)\b',
        r'\b\d+\s+[A-Za-z0-9\s,]+(?:Trail|Tr|Parkway|Pkwy|Circle|Cir)\b'
    ]
    for pattern in address_patterns:
        text = re.sub(pattern, '[ADDRESS REDACTED]', text)
    
    # WhatsApp/Telegram number patterns
    text = re.sub(r'\b(?:whatsapp|telegram|signal|viber)(?:\s+at)?\s+[+]?\d[0-9\s-]{7,}', '[CONTACT REDACTED]', text)
    
    # LinkedIn profile patterns
    text = re.sub(r'linkedin\.com/in/[a-zA-Z0-9_-]+', '[LINKEDIN REDACTED]', text)
    
    # Other social media handles
    text = re.sub(r'@\w{2,}', '[SOCIAL MEDIA HANDLE REDACTED]', text)
    
    return text

@router.post("/")
async def chat_endpoint(request: Request):
    start_time = time.time()
    data = await request.json()
    prompt = data.get("message")
    session_id = data.get("session_id", "anonymous")
    user_id = data.get("user_id", "default_user")
    is_guest = data.get("is_guest", False)

    if not prompt:
        return {"error": "No message provided"}

    clean_prompt = scrub_pii(prompt)

    if not is_career_related(clean_prompt):
        return generate_career_related_response()

    anon_id = generate_anonymous_id(request, session_id)
    if is_gender_biased(clean_prompt):
        return generate_gender_bias_response()

    messages = prepare_context_messages(clean_prompt, anon_id, user_id, is_guest)

    try:
        reply_text, guardrail_intervened = generate_reply(clean_prompt, messages)
    except Exception as e:
        return {"error": str(e), "processing_time_ms": int((time.time() - start_time) * 1000)}

    clean_reply_text = scrub_pii(reply_text)

    if not guardrail_intervened:
        store_context_data(clean_prompt, clean_reply_text, anon_id, user_id, is_guest)

    return {
        "reply": clean_reply_text,
        "guardrail_intervened": guardrail_intervened,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }


def generate_career_related_response():
    return {
        "reply": (
            "I'm designed to help with career-related questions and professional development. "
            "Could you please ask me something about job searching, skill development, "
            "resume building, interviews, or professional growth?"
        ),
        "guardrail_intervened": True
    }


def generate_anonymous_id(request, session_id):
    client_ip = request.client.host
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    return context_manager.get_anonymous_id(session_id, ip_hash)


def generate_gender_bias_response():
    return {
        "reply": (
            "⚠️ This query contains potential gender bias. "
            "At Disha AI, we promote respectful, inclusive dialogue.\n\n"
            "Would you like to rephrase your question?\n\n"
            "💡 Example: try *'How can we support women in tech leadership roles?'*"
        ),
        "guardrail_intervened": True
    }


def prepare_context_messages(clean_prompt, anon_id, user_id, is_guest):
    messages = []
    if not is_guest:
        messages = fetch_authenticated_user_context(anon_id, user_id)
    else:
        messages = fetch_guest_user_context(anon_id)
    messages.append({"role": "user", "content": clean_prompt})
    return messages


def fetch_authenticated_user_context(anon_id, user_id):
    messages = []
    ephemeral_context = context_manager.get_context(anon_id)
    past = fetch_chat_history(user_id, limit=5)
    messages = add_context_messages(ephemeral_context, messages)
    if not messages and past:
        messages = add_context_messages(reversed(past[-6:]), messages)
    return messages


def fetch_guest_user_context(anon_id):
    messages = []
    ephemeral_context = context_manager.get_context(anon_id)
    return add_context_messages(ephemeral_context, messages)


def add_context_messages(context, messages):
    context_list = list(context)
    
    for ctx in context_list[-6:]:
        
        if isinstance(ctx, dict) and "context" in ctx and "prompt" in ctx["context"] and "response" in ctx["context"]:
            messages.append({"role": "user", "content": ctx["context"]["prompt"]})
            messages.append({"role": "assistant", "content": ctx["context"]["response"]})
    
    return messages


def generate_reply(clean_prompt, messages):
    if any(keyword in clean_prompt.lower() for keyword in [
        "job", "jobs", "opening", "hiring", "apply", "remote", "vacancy",
        "mentor", "mentorship", "career guidance", "find a mentor", "coaching",
        "community", "forum", "group", "network", "connect with others",
        "list of jobs", "active jobs", "job listings", "available positions"]):
        reply_text = ask_disha_with_tools(clean_prompt)
        guardrail_intervened = False
    else:
        result = ask_bedrock(messages)
        reply_text = next((r["text"] for r in result["reply"] if r["type"] == "text"), "[No valid text reply]")
        guardrail_intervened = result.get("guardrail_intervened", False)
    return reply_text, guardrail_intervened


def store_context_data(clean_prompt, clean_reply_text, anon_id, user_id, is_guest):
    if not is_guest:
        save_chat(user_id, clean_prompt, clean_reply_text)
    context_manager.store_context(anon_id, {
        'prompt': clean_prompt,
        'response': clean_reply_text,
        'timestamp': datetime.now().isoformat()
    })