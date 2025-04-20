from fastapi import APIRouter, Request
from app.services.bedrock import ask_bedrock

router = APIRouter()

@router.post("/")
async def get_response(request: Request):
    body = await request.json()
    query = body.get("message")
    reply = ask_bedrock(query)
    return {"reply": reply}
