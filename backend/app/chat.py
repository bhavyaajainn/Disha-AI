from fastapi import APIRouter, Request
from services.supabase import fetch_chat_history, save_chat
from services.model_selector import select_model
from services.langchain.agent import ask_disha_with_tools
from services.bedrock import ask_bedrock
from services.bias_detector import is_gender_biased

router = APIRouter()

FALLBACK_GUARDRAIL_RESPONSE = "Sorry, I can't help with that. Let's focus on career-related questions instead."

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("message")
    user_id = data.get("user_id", "default_user")

    if not prompt:
        return {"error": "No message provided"}
    
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

    past = fetch_chat_history(user_id, limit=5)
    messages = []

    for h in reversed(past):
        if h["response"].strip() != FALLBACK_GUARDRAIL_RESPONSE:
            messages.append({"role": "user", "content": h["prompt"]})
            messages.append({"role": "assistant", "content": h["response"]})
            break 

    messages.append({"role": "user", "content": prompt})

    try:
        if any(keyword in prompt.lower() for keyword in [
            "job", "jobs", "opening", "hiring", "apply", "remote", "vacancy",
            "mentor", "mentorship", "career guidance", "find a mentor", "coaching",
            "community", "forum", "group", "network", "connect with others"]):
            # Modified to pass the prompt directly without adding bias persistence
            reply_text = ask_disha_with_tools(prompt)
            guardrail_intervened = False
        else:
            result = ask_bedrock(messages)
            reply_text = next((r["text"] for r in result["reply"] if r["type"] == "text"), "[No valid text reply]")
            guardrail_intervened = result.get("guardrail_intervened", False)
    except Exception as e:
        return {"error": str(e)}

    if not guardrail_intervened:
        save_chat(user_id, prompt, reply_text)

    return {
        "reply": reply_text,
        "guardrail_intervened": guardrail_intervened
    }