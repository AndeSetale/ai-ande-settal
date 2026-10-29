"""
Configuration globale de l'application FastAPI.
Ce fichier charge les variables d'environnement (.env) et définit la classe Settings.
"""

import os
from dotenv import load_dotenv

# Chargement automatique des variables d'environnement depuis le fichier .env
load_dotenv()


class Settings:
    """
    Classe de configuration contenant toutes les variables globales du microservice IA.
    Chaque paramètre tente de lire une variable .env ou utilise une valeur par défaut sécurisée.
    """
    # Port réseau et hôte sur lesquels s'exécute le microservice FastAPI
    PORT: int = int(os.getenv("PORT", 8001))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Clé d'API et modèle pour la Vision Artificielle (Hugging Face)
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_VISION_MODEL: str = os.getenv("HF_VISION_MODEL", "google/vit-base-patch16-224")

    # Clé d'API et modèle pour la génération de texte LLM (OpenRouter)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

    # Dossier de persistance pour la base de données vectorielle ChromaDB RAG
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")


# Instance unique de configuration réutilisable dans l'ensemble des modules du projet
settings = Settings()
