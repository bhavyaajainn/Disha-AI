🚀 Disha AI
Disha AI is an ethical AI-powered career growth assistant that helps users discover jobs, mentorship programs, career advice, and events — with a strong focus on privacy, inclusivity, and fast, reliable interactions.

📚 Project Overview
Disha AI enables users to interact in a natural, safe, and human-like manner, offering:

Real-time job and event discovery.

Career mentorship suggestions.

Inclusive, bias-redirected career advice.

Privacy-first anonymous chat (Guest mode).

Contextual memory for logged-in users.

🛠️ Technical Architecture

Technology Stack-
Frontend:	Next.js, TypeScript, Material-UI	Responsive UI, chat interface, login/signup flow,
Backend:	FastAPI (Python)	Handle chat requests, integrate NLP and APIs,
Authentication:	Supabase	User authentication and session handling,
NLP Engine:	Claude 3 via AWS Bedrock	Natural Language Understanding and Response Generation,
Context Routing:	LangChain	Smart routing of queries and managing flows,
Database:	Supabase (PostgreSQL)	(Optional) Session management, analytics,
Hosting:	Vercel (Frontend), Render (Backend)	Scalable, fast, and secure deployment,

🔥 Why These Technologies Were Chosen

Technology / Model	Reason for Selection
Next.js-	SEO-friendly, fast, server-side rendering, scalable frontend.
TypeScript-	Strong typing for safer, maintainable frontend development.
Material-UI-	Pre-built, accessible UI components.
FastAPI-	High-performance async API server in Python.
Supabase-	Open-source Firebase alternative for quick auth and database.
Claude 3 (AWS Bedrock)-	Reliable, safe LLM responses ensuring inclusivity.
LangChain-	Efficiently routes queries between APIs, LLM, and fallback flows.
Render & Vercel-	Easy and scalable hosting for backend and frontend respectively.

⚙️ How to Run Disha AI Locally
Frontend Setup (Next.js),
git clone <frontend-repo-url>,
cd frontend,
npm install,
Create a .env.local file:
NEXT_PUBLIC_SUPABASE_URL=<your_supabase_url>,
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your_supabase_anon_key>,
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000,

Run the development server:
npm run dev

Access the app at:
http://localhost:3000

Backend Setup (FastAPI)
git clone <backend-repo-url>,
cd backend,
python3 -m venv venv,
source venv/bin/activate,
pip install -r requirements.txt,
Create a .env file:
BEDROCK_ACCESS_KEY=<your_aws_access_key>, 
BEDROCK_SECRET_KEY=<your_aws_secret_key>, 
SUPABASE_URL=<your_supabase_url>, 
SUPABASE_SERVICE_ROLE_KEY=<your_supabase_service_key>

Run the server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Backend will be available at:
http://localhost:8000

🌐 How to Integrate Disha AI with Any Website

Option 1: iFrame Embedding

<iframe 
  src="https://disha-ai.vercel.app"
  style="width: 100%; height: 600px; border: none;">
</iframe>


Option 2: API-Based Integration
POST /chat

Request Body:
{
  "user_input": "Suggest remote jobs for freshers."
}

Response Body:
{
  "bot_response": "Here are some remote jobs you can apply for..."
}

Useful if you want to fully customize your frontend experience.

🔒 Security and Privacy

HTTPS enforced for all frontend-backend communications.

Supabase manages secure authentication and authorization.

No personally identifiable information (PII) stored inside chatbot sessions.

Guest users enjoy full anonymity but without context memory.

📈 Deployment Details:
Component	Platform
Frontend (Next.js)-	Vercel,
Backend (FastAPI)-	Render,
Authentication / Database-	Supabase

🎯 Conclusion:
Disha AI is a highly scalable, ethical, and privacy-focused AI chatbot built to empower users in their career journeys.
It can be easily integrated into educational platforms, career portals, or used as a standalone service to promote professional growth.

