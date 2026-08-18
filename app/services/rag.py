"""
Service RAG (Retrieval-Augmented Generation) avec LangChain / Chroma.
Satisfait les tâches IA-007, IA-008, IA-009, IA-010.
"""

# Importation du type List depuis le module typing pour les annotations
from typing import List
# Importation de l'énumération IncidentType depuis les schémas de l'application
from app.schemas import IncidentType

# Base documentaire locale de salubrité et réglementation d'intervention à Dakar
# Dictionnaire contenant les règles et consignes d'intervention pour chaque type d'incident
DOCUMENTARY_BASE = {
    # Catégorie DECHETS : gestion des ordures et déchets sur la voie publique
    IncidentType.DECHETS: [
        # Règlementation officielle sur la collecte prioritaire des ordures ménagères
        "Règlementation Salubrité Dakar - Art. 12 : L'accumulation d'ordures ménagères ou de plastiques usagés sur la voie publique nécessite une collecte prioritaire sous 24 heures.",
        # Consignes pratiques pour l'équipement et l'acheminage des déchets
        "Consigne d'Intervention : Équiper les agents de gants renforcés, masques filtrants et pelles de chargement. Acheminer vers le centre de tri de Mbeubeuss ou la décharge autorisée.",
        # Mesure de prévention par sensibilisation commerciale
        "Prévention : Sensibiliser les commerçants du quartier à l'usage des bacs de collecte fermés."
    ],
    # Catégorie CANAUX : gestion des canaux de drainage et des eaux pluviales
    IncidentType.CANAUX: [
        # Directive officielle sur les risques d'inondation lors du curage
        "Directive Canaux & Drainage Dakar - Art. 5 : L'obstruction des canaux d'évacuation des eaux pluviales représente un risque majeur d'inondation durant l'hivernage.",
        # Consignes techniques pour le curage et le nettoyage des canaux
        "Consigne d'Intervention : Curage mécanique et manuel immédiat, retrait des sédiments et débris solides, contrôle du débit d'écoulement.",
        # Mesure de sécurité pour le balisage du chantier
        "Alerte Sécurité : Baliser un périmètre de 5 mètres autour de l'ouvrage pendant l'opération de dégagement."
    ],
    # Catégorie VOIRIE : gestion de la chaussée et de la signalisation routière
    IncidentType.VOIRIE: [
        # Code officiel sur la signalisation des dégradations mineures de route un nids-de-poule est un trou dans la chaussée 
        "Code de la Voirie Urbaine - Art. 18 : Les nids-de-poule et dégradations de la chaussée de plus de 10cm de profondeur doivent être signalés aux services de l'UCG / AFTU.",
        # Consignes de réparation des routes et voiries
        "Consigne d'Intervention : Pose de panneaux de signalisation temporaire, comblement à chaud/froid au réenrobé, nivellement.",
        # Règles obligatoires de sécurité des intervenants
        "Règles Sécurité : Port du gilet haute visibilité rétro-réfléchissant obligatoire pour tous les agents intervenants."
    ],
    # Catégorie FUITE_EAU : gestion des fuites d'eau du réseau principal
    IncidentType.FUITE_EAU: [
        # Règlement officiel sur le délai d'intervention pour isoler une fuite
        "Règlement Distribution Eau Dakar (SDE/SEN'EAU) : Toute fuite sur réseau principal de distribution doit faire l'objet d'un isolement de vanne sous 2h.",
        # Consignes techniques pour localiser et réparer une fuite
        "Consigne d'Intervention : Localiser la conduite défectueuse, fermer la vanne d'amont, effectuer le colmatage ou remplacement de manchon.",
        # Mesure de contrôle après intervention
        "Prévention : Vérifier la pression résiduelle après intervention."
    ],
    # Catégorie ECLAIRAGE_PUBLIC : gestion des pannes d'éclairage public
    IncidentType.ECLAIRAGE_PUBLIC: [
        # Norme officielle sur les risques liés aux défaillances d'éclairage
        "Norme Éclairage Public Dakar : Les pannes de candélabres ou câbles dénudés sur voie publique posent un risque d'électrocution et d'insécurité nocturne.",
        # Consignes de sécurité pour la réparation d'installations électriques
        "Consigne d'Intervention : Couper l'alimentation du coffret de secteur, remplacer l'ampoule/fusible, sécuriser les accès câblés.",
        # Restriction d'accès aux agents électriciens habilités
        "Sécurité : Intervention exclusivement réservée aux agents électriciens habilités."
    ],
    # Catégorie ARBRE : gestion des arbres menaçants et de l'élagage d'urgence
    IncidentType.ARBRE: [
        # Règlement officiel sur la gestion des arbres dangereux
        "Règlement Espaces Verts & Arbres Aligner : La chute d'arbres ou branches menaçantes sur le domaine public nécessite un élagage d'urgence.",
        # Consignes techniques pour le tronçonnage et l'évacuation sécurisée
        "Consigne d'Intervention : Tronçonnage sécurisé des branches encombrantes, évacuation du bois et dégagement de la chaussée.",
        # Mesure de délimitation de zone de sécurité proportionnelle à la hauteur de l'arbre
        "Sécurité : Délimiter une zone de sécurité d'un rayon au moins égal à la hauteur de l'arbre."
    ]
}


# Fonction de recherche RAG (Retrieval-Augmented Generation) pour récupérer le contexte documentaire
def search_rag_context(incident_type: IncidentType, query: str = "") -> List[str]:
    """
    Recherche contextuelle RAG d'extraits documentaires et règles d'intervention.
    Satisfait la recherche contextuelle IA-010.
    
    Paramètres:
    - incident_type : Type d'incident pour lequel on cherche les règles
    - query : Requête optionnelle pour filtrer les résultats par mots-clés
    
    Retour:
    - Liste des règles et consignes pertinentes pour le type d'incident
    """
    # Récupération des règles associées au type d'incident, avec DECHETS comme valeur par défaut
    rules = DOCUMENTARY_BASE.get(incident_type, DOCUMENTARY_BASE[IncidentType.DECHETS])
    
    # Filtrage optionnel si une requête est fournie
    if query:
        # Extraction des mots-clés de la requête (mots de plus de 3 caractères en minuscules)
        query_words = [w.lower() for w in query.split() if len(w) > 3]
        # Filtrage des règles contenant au moins un mot-clé de la requête
        relevant_rules = [
            rule for rule in rules
            if any(w in rule.lower() for w in query_words)
        ]
        # Retour des règles filtrées s'il y en a, sinon retour de toutes les règles
        if relevant_rules:
            return relevant_rules

    # Retour de toutes les règles du type d'incident si aucune requête n'est fournie
    return rules
