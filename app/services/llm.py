"""
Service de génération de texte par LLM (Large Language Model) via l'API OpenRouter.
Génère la description synthétique et professionnelle pour le rapport citoyen
ainsi que les préconisations d'intervention pratiques pour les équipes techniques de la Mairie.
"""

import requests
from typing import List
from app.config import settings
from app.schemas import IncidentType, NiveauUrgence


def generate_llm_description_and_recommendations(
    incident_type: IncidentType,
    score_confiance: float,
    niveau_urgence: NiveauUrgence,
    regles_rag: List[str]
) -> tuple[str, str]:
    """
    Fonction principale faisant appel au modèle LLM Meta Llama 3.1 8B via OpenRouter.
    
    Étapes :
    1. Si aucune clé OpenRouter valide n'est configurée, bascule sur le fallback local.
    2. Construit un prompt structuré incluant les informations de l'image et les règles RAG.
    3. Effectue la requête HTTP POST vers l'API OpenRouter.
    4. Extrait et sépare la DESCRIPTION du rapport et les RECOMMANDATIONS terrain.
    
    Paramètres :
        incident_type (IncidentType) : Le type d'incident détecté.
        score_confiance (float) : Le score de certitude entre 0.0 et 1.0.
        niveau_urgence (NiveauUrgence) : Le niveau d'urgence calculé.
        regles_rag (List[str]) : La liste des arrêtés municipaux et lois applicables à Dakar.
        
    Retourne :
        tuple[str, str] : (Description synthétique, Recommandations d'intervention).
    """
    # Vérification de la présence d'une clé API OpenRouter réelle
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("sk-or-v1-demo"):
        return _fallback_llm_generation(incident_type, score_confiance, niveau_urgence, regles_rag)

    # Assemblage des règles RAG sous forme de liste puces pour le prompt
    context_str = "\n".join(f"- {rule}" for rule in regles_rag)
    
    # Prompt système détaillé guidant le modèle LLM sur le rôle et le format de réponse exact
    prompt = f"""
Vous êtes l'Assistant IA officiel de la plateforme de gestion de salubrité urbaine 'Andë Sétal' à Dakar.
Analyse d'image effectuée :
- Type d'incident détecté : {incident_type.value}
- Indice de confiance : {int(score_confiance * 100)}%
- Niveau d'urgence : {niveau_urgence.value}

Directives de la base documentaire RAG :
{context_str}

Consignes de réponse :
Rédigez une réponse structurée en français sous le format exact :
DESCRIPTION: <Une description professionnelle et claire de l'incident en 2 phrases pour le rapport citoyen>
RECOMMANDATIONS: <3 consignes pratiques précises d'intervention pour les agents de terrain>
"""

    try:
        # Endpoint de création de chat completion d'OpenRouter
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://andesetale.sn",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.4  # Température modérée garantissant la cohérence et la précision des consignes
        }
        
        # Envoi de la requête réseau avec un délai d'expiration de 12 secondes
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            
            # Découpage du texte retourné par le LLM selon les balises DESCRIPTION et RECOMMANDATIONS
            description = ""
            recommandations = ""
            for line in content.split("\n"):
                if line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()
                elif line.startswith("RECOMMANDATIONS:"):
                    recommandations = line.replace("RECOMMANDATIONS:", "").strip()

            if description and recommandations:
                return description, recommandations
            else:
                # Retour de découpage par précaution si les balises exactes manquent
                return content[:150], content[150:]

    except Exception as e:
        print(f"[LLM OpenRouter Warning] Fallback déterministe utilisé : {e}")

    # Exécution du fallback déterministe si l'API externe échoue
    return _fallback_llm_generation(incident_type, score_confiance, niveau_urgence, regles_rag)


def _fallback_llm_generation(
    incident_type: IncidentType,
    score_confiance: float,
    niveau_urgence: NiveauUrgence,
    regles_rag: List[str]
) -> tuple[str, str]:
    """
    Génération locale déterministe.
    Permet au serveur de rédiger des rapports citoyen et fiches techniques impeccables
    même sans connexion Internet ou sans clé OpenRouter.
    """
    # Dictionnaire de descriptions riches par catégorie d'incident
    type_labels = {
        IncidentType.DECHETS: "accumulation importante de déchets solides et résidus urbains",
        IncidentType.CANAUX: "obstruction critique des réseaux d'évacuation d'eau pluviale",
        IncidentType.VOIRIE: "dégradation prononcée de la chaussée et nid-de-poule",
        IncidentType.FUITE_EAU: "fuite d'eau apparente provoquant une stagnation sur la voie publique",
        IncidentType.ECLAIRAGE_PUBLIC: "dysfonctionnement de candélabre ou câble électrique exposé",
        IncidentType.ARBRE: "chute de branche ou végétation menaçant la circulation"
    }

    desc_detail = type_labels.get(incident_type, "incident urbain affectant la salubrité")
    
    # 1. Construction de la description professionnelle
    description = (
        f"Signalement d'une {desc_detail} identifié avec une certitude de {int(score_confiance * 100)}%. "
        f"Incident classifié prioritaire sous l'urgence {niveau_urgence.value}."
    )

    # 2. Construction des 3 recommandations d'intervention pratiques
    recomms = (
        f"1. Dépêcher l'équipe d'intervention spécialisée ({incident_type.value}).\n"
        f"2. {regles_rag[1] if len(regles_rag) > 1 else 'Appliquer les consignes de sécurité et baliser la zone.'}\n"
        f"3. Prendre une photo de confirmation avant et après la résolution du problème."
    )

    return description, recomms
