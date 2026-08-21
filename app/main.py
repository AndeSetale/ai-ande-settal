"""
Point d'entrée principal de l'application FastAPI du microservice IA Andë Sétal.
Initialise le serveur, configure la politique de sécurité CORS et inclut les routes d'API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.config import settings

# Instanciation de l'application FastAPI principale avec ses métadonnées Swagger UI
app = FastAPI(
    title="Andë Sétal — Microservice IA",
    description="Microservice FastAPI pour l'analyse d'incidents urbains (Vision, RAG, LLM OpenRouter)",
    version="1.0.0",
)

# Configuration de la politique CORS (Cross-Origin Resource Sharing)
# Permet au Backend Django (Port 8000) et au Frontend Angular (Port 4200) de communiquer sans être bloqués
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Autorise toutes les origines distantes en développement
    allow_credentials=True,    # Autorise l'envoi de cookies et d'entêtes d'autorisation
    allow_methods=["*"],        # Autorise toutes les méthodes HTTP (GET, POST, OPTIONS...)
    allow_headers=["*"],        # Autorise tous les entêtes HTTP
)

# Enregistrement des routes de l'API (Endpoint /analyze-image)
app.include_router(api_router)


@app.get("/health", tags=["Santé"])
def health_check():
    """
    Endpoint de contrôle de santé (Health Check) du microservice IA.
    Permet au Backend et aux outils de monitoring de vérifier que l'IA est en ligne.
    """
    return {
        "status": "online",
        "service": "Microservice IA Andë Sétal",
        "vision_model": settings.HF_VISION_MODEL,
        "llm_model": settings.OPENROUTER_MODEL,
    }
