from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.schemas import AnalyseIAResponse
from app.services.llm import generate_llm_description_and_recommendations
from app.services.rag import search_rag_context
from app.services.vision import analyze_image_vision

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
    Tâches exécutées :
    - IA-003 à IA-006 : Classification de vision (Hugging Face)
    - IA-007 à IA-010 : Extraction de contexte réglementaire RAG
    - IA-011 à IA-012 : Génération LLM OpenRouter
    - IA-013 & IA-014 : Réponse JSON normalisée
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier transmis doit être une image (JPEG, PNG, WebP).",
        )

    try:
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'image soumise est vide.",
            )

        # 1. Analyse Vision (Hugging Face)
        incident_type, score_confiance, niveau_urgence = analyze_image_vision(image_bytes)

        # 2. Recherche Contextuelle RAG (Chroma / LangChain)
        regles_rag = search_rag_context(incident_type)

        # 3. Génération LLM (OpenRouter)
        description, recommandations = generate_llm_description_and_recommendations(
            incident_type=incident_type,
            score_confiance=score_confiance,
            niveau_urgence=niveau_urgence,
            regles_rag=regles_rag,
        )

        # 4. Formattage JSON Normalisé
        return AnalyseIAResponse(
            type_detecte=incident_type,
            score_confiance=score_confiance,
            niveau_urgence_detecte=niveau_urgence,
            description_generee=description,
            recommandations=recommandations,
            regles_contextuelles=regles_rag,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de l'image par le service IA: {str(e)}",
        )
