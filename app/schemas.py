"""
Schémas de données Pydantic et énumérations du projet Andë Sétal.
Définit les contrats d'interface JSON stricts échangés entre FastAPI et le Backend Django.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    """
    Énumération stricte des 6 catégories d'incidents urbains gérés par la plateforme.
    Permet la qualification automatique par le module Computer Vision.
    """
    DECHETS = "DECHETS"                  # Dépôts sauvages, bacs débordants, résidus solides
    CANAUX = "CANAUX"                    # Obstruation de caniveaux, canaux de drainage pluvial
    VOIRIE = "VOIRIE"                    # Nids-de-poule, chaussée dégradée, trottoirs cassés
    ECLAIRAGE_PUBLIC = "ECLAIRAGE_PUBLIC"# Candélabres en panne, fils électriques exposés
    ARBRE = "ARBRE"                      # Branches menaçantes, arbres tombés sur la voie
    FUITE_EAU = "FUITE_EAU"              # Ruptures de canalisation, fuites d'eau propres/usées


class NiveauUrgence(str, Enum):
    """
    Énumération stricte des 4 niveaux de priorité et d'urgence opérationnelle.
    Utilisé par la Mairie pour déterminer le délai de résolution SLA (Service Level Agreement).
    """
    CRITIQUE = "CRITIQUE"  # Intervention d'urgence sous 2h à 24h (Inondations, fuites majeures)
    ELEVE = "ELEVE"        # Intervention rapide sous 48h (Dépôts d'ordures importants, voirie)
    MODERE = "MODERE"      # Intervention planifiée (Éclairage public défectueux)
    ROUTINE = "ROUTINE"    # Maintenance préventive standard


class AnalyseIAResponse(BaseModel):
    """
    Schéma JSON normalisé de réponse pour l'analyse IA d'un incident.
    Structure complète renvoyée au Backend Django après traitement Vision + RAG + LLM.
    """
    type_detecte: IncidentType = Field(
        ..., description="Type d'incident urbain détecté automatiquement par le modèle de vision"
    )
    score_confiance: float = Field(
        ..., description="Score de certitude/confiance calculé par le modèle entre 0.0 et 1.0 (ex: 0.96 pour 96%)"
    )
    niveau_urgence_detecte: NiveauUrgence = Field(
        ..., description="Niveau d'urgence calculé automatiquement (CRITIQUE, ELEVE, MODERE, ROUTINE)"
    )
    description_generee: str = Field(
        ..., description="Description synthétique et professionnelle générée par le LLM pour le rapport citoyen"
    )
    recommandations: str = Field(
        ..., description="Directives et conseils d'intervention pratiques pour les agents de terrain"
    )
    regles_contextuelles: Optional[List[str]] = Field(
        default=[], description="Extraits de règles d'hygiène et lois de salubrité de Dakar issus de la base RAG"
    )
