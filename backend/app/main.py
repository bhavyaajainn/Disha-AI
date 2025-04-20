from fastapi import FastAPI
from services import bedrock  
from app import chat
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://disha-ai.vercel.app", "https://disha-ai.onrender.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "🚀 Disha AI backend running!"}
