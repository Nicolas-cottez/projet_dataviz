# Dictionnaire des Données - Online Retail II

Ce document décrit les variables présentes dans le fichier `data/processed/online_retail_cleaned.csv`.

| Variable | Type | Description | Exemple |
|---|---|---|---|
| **Invoice** | String | Numéro de facture. Un code à 6 chiffres. Si ce code commence par la lettre 'C', cela indique une annulation. | `536365`, `C536379` |
| **StockCode** | String | Code produit (article). Un code à 5 chiffres unique pour chaque produit distinct. | `85123A` |
| **Description** | String | Nom du produit (article). | `WHITE HANGING HEART T-LIGHT HOLDER` |
| **Quantity** | Integer | Les quantités de chaque produit (article) par transaction. | `6` |
| **InvoiceDate** | Datetime | La date et l'heure de génération de chaque transaction. | `2010-12-01 08:26:00` |
| **Price** | Float | Prix unitaire. Prix du produit par unité en livres sterling (£). | `2.55` |
| **Customer ID** | Integer | Numéro client. Un code à 5 chiffres unique pour chaque client. | `17850` |
| **Country** | String | Nom du pays. Le nom du pays où réside chaque client. | `United Kingdom` |
| **TotalAmount** | Float | Montant total de la ligne de commande (`Quantity` * `Price`). | `15.30` |

## Notes sur le Nettoyage

- Les lignes sans `Customer ID` ont été supprimées.
- Les doublons complets ont été traités.
- Les transactions avec des prix négatifs (hors ajustements légitimes) ont été filtrées.
- Le format de date a été standardisé.
