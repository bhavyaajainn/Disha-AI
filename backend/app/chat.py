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
    """Check if the query is related to careers, jobs, or professional development"""
    # Explicit non-career topics that should be rejected
    non_career_topics = [
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
    
    # Explicit list request formats
    list_patterns = [
        r"list of .+",
        r"list .+ songs",
        r"list .+ movies",
        r"show me .+ list",
        r"give me list of .+",
        r"what are the .+ songs",
        r"top \d+ .+"
    ]
    
    text_lower = text.lower().strip()
    
    # Check for list patterns
    for pattern in list_patterns:
        if re.match(pattern, text_lower) and not any(career_term in text_lower for career_term in ["job", "career", "skill", "course", "training", "resume", "cv"]):
            for topic in non_career_topics:
                if topic in text_lower:
                    return False
    
    # Immediately reject if query directly asks about explicit non-career terms
    for topic in non_career_topics:
        if topic in text_lower and len(text_lower.split()) < 10:
            # For short queries containing non-career topics
            return False
    
    # Reject if query clearly asks about a non-career topic
    for topic_phrase in ["tell me about " + topic for topic in non_career_topics]:
        if topic_phrase in text_lower:
            return False
    
    # More comprehensive list of career-related terms
    career_keywords = [
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
    
    # Career-related phrases that might not contain individual keywords
    career_phrases = [
        "going back to work", "return to work", "change my career", 
        "looking for a job", "find a job", "get hired", "get a job",
        "career change", "earn more", "switch careers", "career advice",
        "professional advice", "working parent", "working mother", "working father",
        "stay at home", "maternity leave", "paternity leave", "career break",
        "employment gap", "resume gap", "returning to workforce", "career transition"
    ]
    
    # Check for career keywords
    if any(keyword in text_lower for keyword in career_keywords):
        return True
    
    # Check for career phrases
    if any(phrase in text_lower for phrase in career_phrases):
        return True
    
    # If the query looks like a question about a topic, give benefit of the doubt
    if text_lower.startswith("how") or text_lower.startswith("what") or text_lower.startswith("when") or text_lower.startswith("where") or text_lower.startswith("why") or text_lower.startswith("who") or text_lower.startswith("can"):
        # But still check if it's clearly non-career
        if any(f"{question} {topic}" in text_lower for question in ["how", "what", "when", "where", "why"] for topic in non_career_topics):
            return False
        return True
    
    # If this is a list request for jobs or other career topics, allow it
    if ("list" in text_lower or "show" in text_lower) and any(career_term in text_lower for career_term in ["job", "career", "skill", "course", "training", "resume", "cv", "company", "opportunity"]):
        return True
    
    # Default to false if doesn't match any condition
    return False

@router.post("/")
async def chat_endpoint(request: Request):
    start_time = time.time()
    data = await request.json()
    prompt = data.get("message")
    session_id = data.get("session_id", "anonymous")
    user_id = data.get("user_id", "default_user")
    is_guest = data.get("is_guest", False)  # Get guest flag from request

    if not prompt:
        return {"error": "No message provided"}
    
    # Check if the message is career-related
    if not is_career_related(prompt):
        return {
            "reply": (
                "I'm designed to help with career-related questions and professional development. "
                "Could you please ask me something about job searching, skill development, "
                "resume building, interviews, or professional growth?"
            ),
            "guardrail_intervened": True
        }
    
    # Create anonymous reference without storing PII
    client_ip = request.client.host
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    anon_id = context_manager.get_anonymous_id(session_id, ip_hash)
    
    current_message_biased = is_gender_biased(prompt)
    
    if current_message_biased:
        return {
            "reply": (
                "⚠️ This query contains potential gender bias. "
                "At Disha AI, we promote respectful, inclusive dialogue.\n\n"
                "Would you like to rephrase your question?\n\n"
                "💡 Example: try *'How can we support women in tech leadership roles?'*"
            ),
            "guardrail_intervened": True
        }

    # Get context differently based on user type
    messages = []
    
    if not is_guest:
        # For authenticated users, get context from both ephemeral storage and database
        ephemeral_context = context_manager.get_context(anon_id)
        past = fetch_chat_history(user_id, limit=5)

        # Use ephemeral context first if available
        ephemeral_messages_added = False
        for ctx in ephemeral_context[-3:]:  # Use last 3 exchanges from ephemeral storage
            if "prompt" in ctx["context"] and "response" in ctx["context"]:
                if ctx["context"]["response"].strip() != FALLBACK_GUARDRAIL_RESPONSE:
                    messages.append({"role": "user", "content": ctx["context"]["prompt"]})
                    messages.append({"role": "assistant", "content": ctx["context"]["response"]})
                    ephemeral_messages_added = True
                    break
        
        # Fall back to database history if no ephemeral context
        if not ephemeral_messages_added:
            for h in reversed(past):
                if h["response"].strip() != FALLBACK_GUARDRAIL_RESPONSE:
                    messages.append({"role": "user", "content": h["prompt"]})
                    messages.append({"role": "assistant", "content": h["response"]})
                    break 
    else:
        # For guest users, use only ephemeral context (which will expire naturally)
        # but don't load from or save to the database
        ephemeral_context = context_manager.get_context(anon_id)
        for ctx in ephemeral_context[-3:]:
            if "prompt" in ctx["context"] and "response" in ctx["context"]:
                if ctx["context"]["response"].strip() != FALLBACK_GUARDRAIL_RESPONSE:
                    messages.append({"role": "user", "content": ctx["context"]["prompt"]})
                    messages.append({"role": "assistant", "content": ctx["context"]["response"]})
                    break

    messages.append({"role": "user", "content": prompt})

    try:
        if any(keyword in prompt.lower() for keyword in [
            "job", "jobs", "opening", "hiring", "apply", "remote", "vacancy",
            "mentor", "mentorship", "career guidance", "find a mentor", "coaching",
            "community", "forum", "group", "network", "connect with others",
            "list of jobs", "active jobs", "job listings", "available positions"]):
            # Modified to pass the prompt directly without adding bias persistence
            reply_text = ask_disha_with_tools(prompt)
            guardrail_intervened = False
        else:
            result = ask_bedrock(messages)
            reply_text = next((r["text"] for r in result["reply"] if r["type"] == "text"), "[No valid text reply]")
            guardrail_intervened = result.get("guardrail_intervened", False)
    except Exception as e:
        return {"error": str(e), "processing_time_ms": int((time.time() - start_time) * 1000)}

    # Store context data - but only for authenticated users
    if not guardrail_intervened:
        # Only store in database for authenticated (non-guest) users
        if not is_guest:
            # Store in database only for authenticated users
            save_chat(user_id, prompt, reply_text)
        
        # Store in ephemeral context manager for both user types
        # This is temporary and will expire after the configured time
        context_manager.store_context(anon_id, {
            'prompt': prompt,
            'response': reply_text,
            'timestamp': datetime.now().isoformat()
        })

    return {
        "reply": reply_text,
        "guardrail_intervened": guardrail_intervened,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }