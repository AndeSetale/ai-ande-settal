"""
Service de Computer Vision (Vision Artificielle).
Reçoit les octets d'une photo d'incident, interroge l'API Hugging Face (Vision Transformer)
et détermine le type d'incident ainsi que son niveau d'urgence.
"""

import io
import requests
from PIL import Image
from app.config import settings
from app.schemas import IncidentType, NiveauUrgence

# Score attribué aux prédictions non fiables (fallback heuristique, étiquette inconnue).
# Volontairement sous le seuil de 0.6 du Backend Django, qui sinon remplacerait
# le type d'incident saisi par le citoyen par cette simple supposition.
FALLBACK_SCORE = 0.5


def analyze_image_vision(image_bytes: bytes) -> tuple[IncidentType, float, NiveauUrgence]:
    """
    Fonction principale d'analyse d'image par Vision Artificielle.
    
    Étapes :
    1. Si une clé HF_TOKEN existe, envoie la photo vers l'API d'Inférence Hugging Face (ViT).
    2. Traduit la prédiction anglaise en type d'incident du projet (ex: 'garbage' -> DECHETS).
    3. Calcule l'urgence opérationnelle en fonction du type et du score de certitude.
    4. Si l'API est absente ou échoue, bascule de manière transparente sur le fallback heuristique.
    
    Paramètres :
        image_bytes (bytes) : Octets bruts de l'image transmise par multipart/form-data.
        
    Retourne :
        tuple[IncidentType, float, NiveauUrgence] : (Type détecté, Score de certitude 0-1, Urgence).
    """
    # URL de l'API d'Inférence Hugging Face pour le modèle sélectionné
    # (l'ancienne URL api-inference.huggingface.co a été retirée par Hugging Face)
    api_url = f"https://router.huggingface.co/hf-inference/models/{settings.HF_VISION_MODEL}"
    # Entête d'autorisation Bearer Token si la clé HF_TOKEN est configurée
    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": "image/jpeg",
    } if settings.HF_TOKEN else {}

    try:
        if settings.HF_TOKEN:
            # Envoi de la photo binaire à l'API de Vision avec un délai d'attente maximum de 10 secondes
            response = requests.post(api_url, headers=headers, data=image_bytes, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, list) and len(results) > 0:
                    # Extraction du premier résultat ayant le score de prédiction le plus élevé
                    top_prediction = results[0]
                    label = top_prediction.get("label", "").lower()
                    score = float(top_prediction.get("score", 0.85))

                    # Mappage du label anglais vers le type d'incident et calcul de l'urgence
                    incident_type = _map_label_to_incident_type(label)
                    if incident_type is None:
                        # Étiquette sans rapport avec un incident : type par défaut, confiance plafonnée
                        incident_type, score = IncidentType.DECHETS, min(score, FALLBACK_SCORE)
                    urgency = _calculate_urgency(incident_type, score)
                    return incident_type, round(score, 2), urgency
    except Exception as e:
        # Journalisation d'avertissement en cas d'erreur de communication ou d'absence de réseau
        print(f"[Vision Service Warning] Hugging Face API fallback utilisé : {e}")

    # Exécution du fallback d'analyse autonome si l'API externe n'est pas disponible
    return _heuristic_vision_fallback(image_bytes)


def _map_label_to_incident_type(label: str) -> IncidentType | None:
    """
    Convertit les étiquettes en anglais produites par le modèle Hugging Face
    en types d'incidents officiels de la plateforme Andë Sétal.
    """
    # Catégorie Déchets & Salubrité
    if any(k in label for k in ["trash", "garbage", "waste", "litter", "rubbish", "plastic", "dump"]):
        return IncidentType.DECHETS
    # Catégorie Fuites d'eau & Canalisations
    elif any(k in label for k in ["water", "pipe", "leak", "flood", "stream", "drainage"]):
        return IncidentType.FUITE_EAU
    # Catégorie Canaux & Évacuation des eaux pluviales
    elif any(k in label for k in ["canal", "sewer", "gully", "channel"]):
        return IncidentType.CANAUX
    # Catégorie Voirie, Nids-de-poule & Chaussée
    elif any(k in label for k in ["pothole", "road", "asphalt", "street", "crack"]):
        return IncidentType.VOIRIE
    # Catégorie Éclairage Public & Électricité
    elif any(k in label for k in ["lamp", "light", "pole", "post", "electricity"]):
        return IncidentType.ECLAIRAGE_PUBLIC
    # Catégorie Arbres & Vegétation
    elif any(k in label for k in ["tree", "branch", "wood", "plant", "foliage"]):
        return IncidentType.ARBRE

    # Aucun mot-clé reconnu : l'appelant décide de la valeur de secours
    return None


def _calculate_urgency(incident_type: IncidentType, score: float) -> NiveauUrgence:
    """
    Règle métier déterminant le niveau d'urgence d'intervention selon
    la gravité intrinsèque du type d'incident et la certitude de détection.
    """
    # Les canaux bouchés et fuites d'eau représentent un risque d'inondation immédiat
    if incident_type in [IncidentType.CANAUX, IncidentType.FUITE_EAU] and score > 0.7:
        return NiveauUrgence.CRITIQUE
    # Les déchets sauvages et nids-de-poule profonds nécessitent un traitement prioritaire sous 48h
    elif incident_type in [IncidentType.DECHETS, IncidentType.VOIRIE] and score > 0.8:
        return NiveauUrgence.ELEVE
    # L'éclairage public défectueux est classé modéré
    elif incident_type == IncidentType.ECLAIRAGE_PUBLIC:
        return NiveauUrgence.MODERE
    # Tout autre incident est traité selon le cycle de routine
    else:
        return NiveauUrgence.ROUTINE


def _heuristic_vision_fallback(image_bytes: bytes) -> tuple[IncidentType, float, NiveauUrgence]:
    """
    Fallback d'analyse visuelle autonome.
    Inspecte les dimensions physiques de l'image (ratio largeur/hauteur) pour garantir
    que le serveur répond instantanément même en cas d'absence d'Internet ou de clé API.
    """
    try:
        # Analyse des métadonnées de l'image grâce à la librairie Pillow (PIL)
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        ratio = width / height if height > 0 else 1.0

        # Heuristique d'orientation de la photo
        if ratio > 1.3:
            incident_type = IncidentType.DECHETS
        else:
            incident_type = IncidentType.VOIRIE

        score = FALLBACK_SCORE
        urgency = _calculate_urgency(incident_type, score)
        return incident_type, score, urgency
    except Exception:
        # Valeur de secours ultime en cas d'erreur de décodage d'image
        return IncidentType.DECHETS, FALLBACK_SCORE, NiveauUrgence.ROUTINE
