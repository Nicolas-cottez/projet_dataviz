# Online Retail II - Marketing Decision Support App

Application d'aide à la décision marketing basée sur le dataset Online Retail II. Permet l'analyse de cohortes, la segmentation RFM, et la simulation de CLV.

## 📂 Structure du Projet

```
.
├── app/
│   ├── app.py           # Point d'entrée de l'application Streamlit
│   ├── utils.py         # Fonctions utilitaires (chargement, calculs, filtres)
│   ├── kpi.py           # Page : KPIs & Overview
│   ├── cohortes.py      # Page : Analyse des Cohortes
│   ├── segments.py      # Page : Segmentation RFM
│   ├── scenarios.py     # Page : Simulation de Scénarios
│   └── action_plan.py   # Page : Exports & Plan d'Action
├── data/
│   ├── raw/             # Données brutes (2009-2010.csv, 2010-2011.csv)
│   └── processed/       # Données nettoyées (online_retail_cleaned.csv)
├── notebooks/
│   └── 01_exploration.ipynb # Notebook d'exploration et d'analyse
├── src/
│   └── process_data.py  # Script de nettoyage des données
├── requirements.txt     # Dépendances Python
├── README.md            # Documentation
└── DATA_DICTIONARY.md   # Dictionnaire des données
```

## 🚀 Installation

1. **Cloner le projet** ou télécharger les fichiers.
2. **Créer un environnement virtuel** (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```
3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Préparation des Données

Si le fichier `data/processed/online_retail_cleaned.csv` n'existe pas, lancez le script de traitement :

```bash
python src/process_data.py
```

Ce script va :
- Fusionner les datasets 2009-2010 et 2010-2011.
- Nettoyer les données (types, manquants).
- Exporter le fichier nettoyé dans `data/processed/`.

## 🖥️ Lancement de l'Application

Exécutez la commande suivante depuis la racine du projet :

```bash
streamlit run app/app.py
```

L'application s'ouvrira dans votre navigateur par défaut (généralement http://localhost:8501).

## 📊 Fonctionnalités

- **KPIs** : Vue d'ensemble du CA, clients actifs, rétention et CLV.
- **Cohortes** : Analyse de la rétention client par mois d'acquisition (Heatmap).
- **Segments** : Segmentation RFM (Recency, Frequency, Monetary) pour identifier les clients VIP, à risque, etc.
- **Scénarios** : Simulateur d'impact sur la CLV en modifiant la marge, la rétention ou le taux d'actualisation.
- **Plan d'Action** : Liste filtrable des clients avec leurs segments pour export CSV.

## 📝 Auteur
Projet Data Visualization - ECE 2025
