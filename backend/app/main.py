from fastapi import FastAPI
from services import bedrock  
from app import chat
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(chat.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🚀 Disha AI backend running!"}
