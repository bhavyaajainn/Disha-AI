from fastapi import FastAPI
from services import bedrock  
from app import chat
from fastapi.middleware.cors import CORSMiddleware
from services.context_manager import EphemeralContextManager

app = FastAPI()
context_manager = EphemeralContextManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://disha-ai.vercel.app", "https://disha-ai.onrender.com", "http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"message": "🚀 Disha AI backend running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}