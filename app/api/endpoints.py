"""
Routeur API principal du microservice IA Andë Sétal.
Expose l'endpoint HTTP POST /analyze-image recevant les photos d'incidents transmises par le Backend Django.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.schemas import AnalyseIAResponse
from app.services.llm import generate_llm_description_and_recommendations
from app.services.rag import search_rag_context
from app.services.vision import analyze_image_vision

# Création du routeur d'API FastAPI
router = APIRouter(prefix="", tags=["Analyse IA"])


@router.post(
    "/analyze-image",
    response_model=AnalyseIAResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse d'image d'incident urbain (Vision + RAG + LLM)",
    description="Endpoint principal qui reçoit la photo d'un incident, détecte le type, évalue l'urgence et génère la description et les recommandations via OpenRouter.",
)
async def analyze_incident_image(file: UploadFile = File(...)):
    """
    Endpoint de traitement principal d'un signalement citoyen par l'IA.
    
    Déroulement complet du traitement :
    1. Validation du type MIME du fichier (doit être une image JPEG, PNG ou WebP).
    2. Phase 1 - Computer Vision (Hugging Face) : Détection de la catégorie d'incident et calcul de l'urgence.
    3. Phase 2 - RAG (Dakar Plateau) : Extraction des règles de salubrité et arrêtés municipaux pertinents.
    4. Phase 3 - LLM (OpenRouter Llama 3.1) : Génération de la description synthétique et des recommandations terrain.
    5. Phase 4 - Formatage JSON : Instanciation et retour du schéma AnalyseIAResponse validé.
    """
    # 1. Vérification que le fichier téléversé est bien une image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier transmis doit être une image (JPEG, PNG, WebP).",
        )

    try:
        # Lecture des octets binaires du fichier transmis
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'image soumise est vide.",
            )

        # 2. Étape 1 : Analyse par Vision Artificielle (Computer Vision)
        incident_type, score_confiance, niveau_urgence = analyze_image_vision(image_bytes)

        # 3. Étape 2 : Extraction du contexte réglementaire RAG (Lois & Arrêtés de Dakar Plateau)
        regles_rag = search_rag_context(incident_type)

        # 4. Étape 3 : Génération de texte par le LLM (OpenRouter / Llama 3.1 8B)
        description, recommandations = generate_llm_description_and_recommendations(
            incident_type=incident_type,
            score_confiance=score_confiance,
            niveau_urgence=niveau_urgence,
            regles_rag=regles_rag,
        )

        # 5. Étape 4 : Assemblage de la réponse JSON normalisée et retour au Backend Django
        return AnalyseIAResponse(
            type_detecte=incident_type,
            score_confiance=score_confiance,
            niveau_urgence_detecte=niveau_urgence,
            description_generee=description,
            recommandations=recommandations,
            regles_contextuelles=regles_rag,
        )

    except HTTPException:
        # Relance des exceptions HTTP spécifiques sans modification
        raise
    except Exception as e:
        # Capture de toute erreur inattendue et retour d'un statut HTTP 500 explicatif
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de l'image par le service IA: {str(e)}",
        )
