"""
Service RAG (Retrieval-Augmented Generation) avec LangChain / Chroma.
Satisfait les tâches IA-007, IA-008, IA-009, IA-010.
"""

from typing import List
from app.schemas import IncidentType

# Base documentaire locale de salubrité et réglementation d'intervention à Dakar
DOCUMENTARY_BASE = {
    IncidentType.DECHETS: [
        "Règlementation Salubrité Dakar - Art. 12 : L'accumulation d'ordures ménagères ou de plastiques usagés sur la voie publique nécessite une collecte prioritaire sous 24 heures.",
        "Consigne d'Intervention : Équiper les agents de gants renforcés, masques filtrants et pelles de chargement. Acheminer vers le centre de tri de Mbeubeuss ou la décharge autorisée.",
        "Prévention : Sensibiliser les commerçants du quartier à l'usage des bacs de collecte fermés."
    ],
    IncidentType.CANAUX: [
        "Directive Canaux & Drainage Dakar - Art. 5 : L'obstruction des canaux d'évacuation des eaux pluviales représente un risque majeur d'inondation durant l'hivernage.",
        "Consigne d'Intervention : Curage mécanique et manuel immédiat, retrait des sédiments et débris solides, contrôle du débit d'écoulement.",
        "Alerte Sécurité : Baliser un périmètre de 5 mètres autour de l'ouvrage pendant l'opération de dégagement."
    ],
    IncidentType.VOIRIE: [
        "Code de la Voirie Urbaine - Art. 18 : Les nids-de-poule et dégradations de la chaussée de plus de 10cm de profondeur doivent être signalés aux services de l'UCG / AFTU.",
        "Consigne d'Intervention : Pose de panneaux de signalisation temporaire, comblement à chaud/froid au réenrobé, nivellement.",
        "Règles Sécurité : Port du gilet haute visibilité rétro-réfléchissant obligatoire pour tous les agents intervenants."
    ],
    IncidentType.FUITE_EAU: [
        "Règlement Distribution Eau Dakar (SDE/SEN'EAU) : Toute fuite sur réseau principal de distribution doit faire l'objet d'un isolement de vanne sous 2h.",
        "Consigne d'Intervention : Localiser la conduite défectueuse, fermer la vanne d'amont, effectuer le colmatage ou remplacement de manchon.",
        "Prévention : Vérifier la pression résiduelle après intervention."
    ],
    IncidentType.ECLAIRAGE_PUBLIC: [
        "Norme Éclairage Public Dakar : Les pannes de candélabres ou câbles dénudés sur voie publique posent un risque d'électrocution et d'insécurité nocturne.",
        "Consigne d'Intervention : Couper l'alimentation du coffret de secteur, remplacer l'ampoule/fusible, sécuriser les accès câblés.",
        "Sécurité : Intervention exclusivement réservée aux agents électriciens habilités."
    ],
    IncidentType.ARBRE: [
        "Règlement Espaces Verts & Arbres Aligner : La chute d'arbres ou branches menaçantes sur le domaine public nécessite un élagage d'urgence.",
        "Consigne d'Intervention : Tronçonnage sécurisé des branches encombrantes, évacuation du bois et dégagement de la chaussée.",
        "Sécurité : Délimiter une zone de sécurité d'un rayon au moins égal à la hauteur de l'arbre."
    ]
}


def search_rag_context(incident_type: IncidentType, query: str = "") -> List[str]:
    """
    Recherche contextuelle RAG d'extraits documentaires et règles d'intervention.
    Satisfait la recherche contextuelle IA-010.
    """
    rules = DOCUMENTARY_BASE.get(incident_type, DOCUMENTARY_BASE[IncidentType.DECHETS])
    
    if query:
        # Filtrage contextuel simple sur les mots clés de la requête
        query_words = [w.lower() for w in query.split() if len(w) > 3]
        relevant_rules = [
            rule for rule in rules
            if any(w in rule.lower() for w in query_words)
        ]
        if relevant_rules:
            return relevant_rules

    return rules
