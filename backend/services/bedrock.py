import boto3
import json
import os
import time
from dotenv import load_dotenv
from services.model_selector import select_model
from botocore.exceptions import ClientError

load_dotenv()

def ask_bedrock(messages: list) -> dict:

    region = os.getenv("AWS_REGION")
    account_id = os.getenv("AWS_ACCOUNT_ID")
    if not region or not account_id:
        raise ValueError("Missing AWS_REGION or AWS_ACCOUNT_ID in env")

    model_id = select_model(messages[-1]["content"])

    bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "max_tokens": 500
    })
    content_type = "application/json"

    guardrail_id = "y97oobg1ywy2"
    guardrail_arn = f"arn:aws:bedrock:{region}:{account_id}:guardrail/{guardrail_id}"

    retries = 3
    for attempt in range(retries):
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body,
                accept="application/json",
                contentType=content_type,
                guardrailIdentifier=guardrail_arn,
                guardrailVersion="DRAFT"
            )

            response_body = response["body"].read()
            decoded = json.loads(response_body)
            final_text = decoded.get("content") or decoded.get("completion", "")
            if isinstance(final_text, list):
                final_text = " ".join(part.get("text", "") for part in final_text)
            fallback_phrases = [
                "Sorry, I can't help with that",
                "I cannot in good conscience",
                "Let's focus on career-related questions"
            ]
            guardrail_intervened = any(p.lower() in final_text.lower() for p in fallback_phrases)

            return {
                "reply": [{"type": "text", "text": final_text.strip()}],  
                "model_used": model_id,
                "guardrail_intervened": guardrail_intervened
            }

        except ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException":
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Client error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error calling Bedrock: {str(e)}")

    raise RuntimeError("Max retries exceeded")
