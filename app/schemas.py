from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    DECHETS = "DECHETS"
    CANAUX = "CANAUX"
    VOIRIE = "VOIRIE"
    ECLAIRAGE_PUBLIC = "ECLAIRAGE_PUBLIC"
    ARBRE = "ARBRE"
    FUITE_EAU = "FUITE_EAU"


class NiveauUrgence(str, Enum):
    CRITIQUE = "CRITIQUE"
    ELEVE = "ELEVE"
    MODERE = "MODERE"
    ROUTINE = "ROUTINE"


class AnalyseIAResponse(BaseModel):
    """
    Schéma JSON normalisé de réponse pour l'analyse IA d'un incident.
    Conforme aux spécifications des tâches IA-004 à IA-014.
    """
    type_detecte: IncidentType = Field(
        ..., description="Type d'incident urbain détecté par le modèle de vision"
    )
    score_confiance: float = Field(
        ..., description="Score de certitude/confiance du modèle entre 0.0 et 1.0"
    )
    niveau_urgence_detecte: NiveauUrgence = Field(
        ..., description="Niveau d'urgence calculé automatiquement (CRITIQUE, ELEVE, MODERE, ROUTINE)"
    )
    description_generee: str = Field(
        ..., description="Description synthétique et professionnelle générée par LLM (OpenRouter)"
    )
    recommandations: str = Field(
        ..., description="Directives et conseils d'intervention générés par RAG/LLM"
    )
    regles_contextuelles: Optional[List[str]] = Field(
        default=[], description="Extraits de règles d'hygiène urbaine issus de la base RAG"
    )
