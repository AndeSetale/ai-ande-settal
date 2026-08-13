import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: int = int(os.getenv("PORT", 8001))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_VISION_MODEL: str = os.getenv("HF_VISION_MODEL", "google/vit-base-patch16-224")

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

settings = Settings()
