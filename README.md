# NLP Mini-Project - Intent Classification for Railway Trajectory Detection

## Description

Ce projet implémente un système de classification d'intentions basé sur le NLP pour détecter les demandes de trajets ferroviaires. Le modèle distingue les requêtes de trajectoires pures des autres types de requêtes liées aux voyages (horaires, billets, prix).

## Objectif

Le modèle fait partie d'un pipeline plus large de recherche d'itinéraires optimaux. Son rôle est de classifier les entrées utilisateur en quatre catégories :

- **TRIP** : Requêtes de trajectoire pure (ex: "De Paris à Lyon", "Je vais de Bordeaux à Marseille")
- **NOT_TRIP** : Requêtes liées au voyage mais pas des trajectoires (horaires, billets, trains disponibles, prix)
- **NOT_FRENCH** : Requêtes dans une langue étrangère
- **UNKNOWN** : Texte incompréhensible ou hors contexte

## Structure du Projet

```
nlp_miniproject/
├── Intent_Classification_CPU.ipynb    # Notebook principal
├── requirements.txt                    # Dépendances Python
├── dataset/
│   ├── train_set.csv                  # Données d'entraînement (8000 exemples)
│   ├── test_set.csv                   # Données de test (2000 exemples)
│   ├── cities_fr.txt                  # Liste des villes françaises
│   ├── sample_nlp_input.txt           # Exemples d'entrées
│   └── sample_nlp_output.txt          # Exemples de sorties attendues
└── Documentation_Detection_Intention_COMPLETE.docx  # Documentation détaillée
```

## Distribution des Données

### Train Set (8000 exemples)
- TRIP: 3200 (40%)
- NOT_TRIP: 2400 (30%)
- NOT_FRENCH: 1600 (20%)
- UNKNOWN: 800 (10%)

### Test Set (2000 exemples)
- TRIP: 800 (40%)
- NOT_TRIP: 600 (30%)
- NOT_FRENCH: 400 (20%)
- UNKNOWN: 200 (10%)

## Distinction TRIP vs NOT_TRIP

### TRIP (Trajets purs)
Requêtes demandant uniquement un trajet d'un point A à un point B, sans mention explicite de trains, billets, horaires ou prix.

Exemples :
- "De Paris à Lyon"
- "Je vais de Bordeaux à Marseille"
- "Strasbourg vers Metz"
- "J'aimerais aller de Nice à Cannes"

### NOT_TRIP (Requêtes voyage non-trajet)
Requêtes mentionnant des trains, billets, horaires, prix, réservations ou disponibilités.

Exemples :
- "Quels sont les horaires pour Paris Lyon ?"
- "Un billet pour Bordeaux Marseille"
- "Y a-t-il des trains disponibles de Nice à Cannes ?"
- "Quel est le prix du trajet Paris Lyon ?"

## Installation

### Prérequis
- Python 3.8+
- GPU (recommandé) ou CPU

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Entraînement du modèle

Ouvrir le notebook `Intent_Classification_CPU.ipynb` et exécuter les cellules séquentiellement :

1. Vérification GPU/CPU
2. Chargement des datasets
3. Prétraitement des données
4. Fine-tuning du modèle d'intent classification
5. Évaluation du modèle
6. Entraînement du modèle NER (reconnaissance d'entités)
7. Pipeline d'inférence complet

### 2. Inférence

```python
# Charger le modèle entraîné
from transformers import pipeline

intent_classifier = pipeline("text-classification", model="./intent_model")
ner_pipeline = pipeline("ner", model="./ner_model")

# Classifier une requête
text = "De Paris à Lyon"
result = intent_classifier(text)
```

## Modèles Utilisés

- **Intent Classification** : CamemBERT (fine-tuné)
- **NER** : CamemBERT (fine-tuné pour extraction d'entités : Departure, Destination)

## Métriques de Performance

### Intent Classification
- Accuracy globale : ~92-95%
- F1 TRIP : 85-90%
- F1 NOT_TRIP : 88-92%
- F1 NOT_FRENCH : 95-98%
- F1 UNKNOWN : 90-93%

### NER
- F1 Departure : 93-96%
- F1 Destination : 93-96%

## Techniques Utilisées

- **Class Weighting** : Gestion du déséquilibre des classes
- **WeightedTrainer** : Custom trainer avec loss pondérée
- **Post-processing** : Règles de validation et correction
- **Entity Extraction** : Identification des villes de départ et d'arrivée

## Scripts de Génération

Le projet inclut des scripts Python pour régénérer les datasets :

- `regenerate_correct_dataset.py` : Génération des datasets avec labels corrects

## Documentation

Une documentation complète de 600+ pages est disponible dans `Documentation_Detection_Intention_COMPLETE.docx`, expliquant ligne par ligne chaque cellule du notebook.

## Auteur

Stanley Honkpehedji

## Licence

Ce projet est à usage éducatif.

## Notes Importantes

- Les datasets ont été régénérés avec des définitions de labels corrigées (octobre 2025)
- Le modèle doit être ré-entraîné sur les nouveaux datasets pour des performances optimales
- La distinction TRIP/NOT_TRIP est critique pour l'intégration dans le pipeline de recherche d'itinéraires
