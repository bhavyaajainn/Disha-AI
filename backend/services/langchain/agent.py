import time
from services.model_selector import select_model
from services.tools.jobs import remote_job_tool
from services.tools.mentorship import mentorship_tool
from services.tools.community import community_tool
from services.bias_detector import is_gender_biased  # Import bias detector
from langchain_community.chat_models import BedrockChat
from langchain.agents import initialize_agent
from langchain_core.runnables import Runnable

def prompt_needs_tool(llm, prompt: str) -> bool:
    prompt_clean = prompt.strip().lower()
    trigger_keywords = [
        "job", "jobs", "opening", "hiring", "apply", "remote", "vacancy",
        "mentor", "mentorship", "career guidance", "find a mentor", "coaching",
        "community", "forum", "group", "network", "connect with others", "communities"
    ]

    if any(keyword in prompt_clean for keyword in trigger_keywords):
        return True

    system_prompt = (
        "You are a classifier. Only respond with 'YES' or 'NO'. "
        "Say 'YES' only if the prompt needs real-time data like job listings, mentorship programs, or community platforms. "
        "Say 'NO' if it's just a general advice or explanation request."
    )

    try:
        routing_response = llm.invoke(f"{system_prompt}\n\nPrompt: {prompt_clean}")
        return "YES" in routing_response.content.strip().upper()
    except Exception:
        return True

def ask_disha_with_tools(prompt: str) -> str:
    # Check only the current prompt for gender bias - no persistence
    if is_gender_biased(prompt):
        return (
            "⚠️ This query contains potential gender bias. "
            "At Disha AI, we promote respectful, inclusive dialogue.\n\n"
            "Would you like to rephrase your question?\n\n"
            "💡 Example: try *'How can we support women in tech leadership roles?'*"
        )

    model_id = select_model(prompt)
    llm = BedrockChat(model_id=model_id, region_name="us-east-1")
    if not prompt_needs_tool(llm, prompt):
        print("💬 Prompt handled directly via LLM (no tools)")
        result = llm.invoke(prompt)
        return str(result.content)

    tools = [remote_job_tool, mentorship_tool, community_tool]
    agent: Runnable = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )

    try:
        tool_query = prompt.strip()
        intermediate_result = agent.invoke({"input": tool_query})
        tool_output = intermediate_result["output"] if isinstance(intermediate_result, dict) else str(intermediate_result)
    except Exception as e:
        return f"⚠️ Error using tools: {str(e)}"

    summarization_prompt = (
        f"The user asked: {prompt}\n\n"
        "Below is structured information from trusted sources (with links):\n\n"
        f"```\n{tool_output}\n```\n\n"
        "Please summarize the results in a helpful, structured format that includes:\n"
        "- Clear key takeaways with bullet points\n"
        "- Important links should be preserved or rephrased as raw URLs\n"
        "- Friendly and concise tone\n"
        "- Avoid repeating everything unless it's useful"
    )

    try:
        summary = llm.invoke(summarization_prompt)
        return str(summary.content if hasattr(summary, "content") else summary)
    except Exception as e:
        return tool_output