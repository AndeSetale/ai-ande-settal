from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="Andë Sétal — Microservice IA",
    description="Microservice FastAPI pour l'analyse d'incidents urbains (Vision, RAG, LLM OpenRouter)",
    version="1.0.0",
)

# Configuration CORS pour autoriser Backend Django et Frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Santé"])
def health_check():
    """Endpoint de contrôle de santé du microservice IA."""
    return {
        "status": "online",
        "service": "Microservice IA Andë Sétal",
        "vision_model": settings.HF_VISION_MODEL,
        "llm_model": settings.OPENROUTER_MODEL,
    }
