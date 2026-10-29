# 🧠 Andë Sétal — Microservice IA FastAPI

Bienvenue dans le dépôt du **Microservice IA** de la plateforme **Andë Sétal** (Co-gestion de la salubrité urbaine pour la Mairie de Dakar Plateau).

Ce microservice est développé avec **FastAPI** et s'appuie sur une architecture hybride à 3 piliers :
1. 👁️ **Computer Vision (Hugging Face / ViT)** : Classification automatique de la photo d'incident (`DECHETS`, `CANAUX`, `VOIRIE`, `FUITE_EAU`, `ECLAIRAGE_PUBLIC`, `ARBRE`) et calcul du score de certitude.
2. 📚 **RAG (Retrieval-Augmented Generation)** : Extraction des règles de salubrité, arrêtés municipaux et consignes de sécurité officielles de Dakar Plateau.
3. 📝 **LLM (OpenRouter / Llama 3.1 8B)** : Rédaction automatique de la synthèse synthétique pour le citoyen et des directives d'intervention pour les agents municipaux.

---

## 📋 Prérequis Système

Avant de commencer, assurez-vous d'avoir installé sur votre machine :
- **Python 3.10** ou version supérieure (`python --version`)
- **Git** (`git --version`)

---

## 🚀 Guide d'Installation Étape par Étape

### 1. Accéder au dossier du projet
Ouvrez votre terminal (PowerShell, Bash ou Invite de commande) et accédez au répertoire :
```bash
cd ai-ande-settal
```

### 2. Créer et activer un environnement virtuel Python

- **Sur Windows (PowerShell)** :
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Sur Linux / macOS** :
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

*(Vous verrez `(.venv)` s'afficher au début de votre ligne de terminal).*

### 3. Installer les dépendances du projet
Exécutez la commande suivante pour installer toutes les librairies requises :
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration du fichier d'environnement `.env`

Créez un fichier nommé **`.env`** à la racine du dossier `ai-ande-settal/` :

```env
# Configuration du Serveur
PORT=8001
HOST=0.0.0.0

# 1. Hugging Face Token (Computer Vision - Optionnel)
HF_TOKEN=hf_votre_token_hugging_face_ici
HF_VISION_MODEL=google/vit-base-patch16-224

# 2. OpenRouter API Key (LLM Llama 3.1 8B - Optionnel)
OPENROUTER_API_KEY=sk-or-v1-votre_cle_openrouter_ici
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free

# 3. Répertoire de persistance RAG
CHROMA_PERSIST_DIR=./data/chroma_db
```

### 💡 Note importante sur le Mode Démo / Fallback
- **Si vous n'avez pas de clé API** : Vous pouvez laisser les valeurs par défaut ou démarrer sans fichier `.env`. Le microservice basculera automatiquement sur son **moteur de fallback autonome local** et fonctionnera à 100% sans aucun blocage !
- **Pour obtenir des clés API gratuites** :
  - **Hugging Face (Vision)** : Gratuit sur [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (Rôle *Read*).
  - **OpenRouter (LLM)** : Gratuit sur [openrouter.ai/keys](https://openrouter.ai/keys).

---

## 🏃 Démarrage du Microservice IA

Pour lancer le serveur en mode développement avec rechargement automatique :

```bash
uvicorn app.main:app --reload --port 8001
```

Vous verrez le message de confirmation :
```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

---

## 🧪 Tests & Vérification

### 1. Tester via l'interface Swagger UI (Interactif)
Ouvrez votre navigateur sur : 👉 **`http://localhost:8001/docs`**

1. Cliquez sur **`POST /analyze-image`** ➔ **"Try it out"**.
2. Sélectionnez une photo d'incident dans le champ `file`.
3. Cliquez sur **"Execute"**.
4. Vous recevrez la réponse JSON enrichie (`type_detecte`, `score_confiance`, `niveau_urgence_detecte`, `description_generee`, `recommandations`).

### 2. Tester l'état du serveur (Health Check)
Ouvrez votre navigateur sur : 👉 **`http://localhost:8001/health`**  
Réponse attendue :
```json
{
  "status": "online",
  "service": "Microservice IA Andë Sétal",
  "vision_model": "google/vit-base-patch16-224",
  "llm_model": "meta-llama/llama-3.1-8b-instruct:free"
}
```

---

## 📁 Architecture du Code Source

```text
app/
├── config.py         # Lecture et centralisation des variables d'environnement
├── schemas.py        # Schémas de validation Pydantic (IncidentType, NiveauUrgence)
├── main.py           # Point d'entrée FastAPI, middleware CORS et route /health
├── api/
│   └── endpoints.py  # Routeur HTTP principal avec l'endpoint POST /analyze-image
└── services/
    ├── vision.py     # Module de classification par Computer Vision (Hugging Face + Fallback)
    ├── rag.py        # Moteur RAG & Base de données des arrêtés de salubrité de Dakar
    └── llm.py        # Module de génération LLM (OpenRouter / Llama 3.1 + Fallback)
```

---

## 🔗 Liaison avec le Backend Django

Ce microservice est conçu pour être interrogé directement par le Backend Django REST Framework (`http://localhost:8000`).

Lorsqu'un citoyen soumet un incident sur l'application mobile, le Backend Django envoie l'image en arrière-plan à `http://localhost:8001/analyze-image` et enregistre le résultat dans la table BDD `AnalyseIA`.
