# Token Tracker 📊

Un outil Python simple pour **enregistrer, suivre et consolider** l'utilisation des tokens par requête pour les modèles de langage (Mistral AI, OpenAI, etc.).

Parfait pour **Jupyter Lab** - il suffit de copier-coller et d'utiliser !

## ✨ Fonctionnalités

- 📝 **Enregistrement des requêtes** : Stocke chaque requête avec ses métadonnées
- 📊 **Consolidation automatique** : Statistiques par jour, par modèle
- 💾 **Persistance** : Sauvegarde dans un fichier JSON
- 📈 **Analyse** : Statistiques détaillées et totaux
- 🐼 **Intégration Pandas** : Export facile vers DataFrame pour visualisation

## 🚀 Installation

### Option 1 : Utilisation directe dans Jupyter Lab

Copiez-collez simplement le contenu de [`token_tracker.py`](token_tracker.py) dans une cellule et utilisez-le directement.

### Option 2 : Installation comme package

```bash
# Cloner le dépôt
git clone https://github.com/jre10/mistral-ai.git
cd mistral-ai/token_tracker

# Installer en mode développement
pip install -e .
```

## 💡 Utilisation

### Exemple de base

```python
from token_tracker import TokenTracker

# Créer un tracker (crée un fichier token_usage.json)
tracker = TokenTracker()

# Enregistrer une requête
tracker.add_request(
    request_name="Analyse de texte",
    prompt_tokens=50,
    completion_tokens=150,
    model="mistral-tiny",
    temperature=0.7
)

# Ajouter une autre requête
tracker.add_request(
    request_name="Traduction FR->EN",
    prompt_tokens=100,
    completion_tokens=80,
    model="mistral-small",
    metadata={"source": "document.pdf", "pages": [1, 2, 3]}
)
```

### Obtenir des statistiques

```python
# Statistiques consolidées par jour (DataFrame)
df_consolidated = tracker.get_consolidated_stats()
print(df_consolidated)

# Utilisation totale
total_usage = tracker.get_total_usage()
print(f"Tokens totaux utilisés : {total_usage['total_tokens']}")

# Détails pour une journée spécifique
df_daily = tracker.get_daily_stats("2024-01-15")
print(df_daily)

# Requêtes par modèle
df_model = tracker.get_requests_by_model("mistral-tiny")
print(df_model)
```

### Export des données

```python
# Exporter vers CSV
tracker.export_to_csv("mon_usage_tokens.csv")

# Accéder aux données brutes
tracker.usage_data  # Dictionnaire avec toutes les données
```

## 📋 Méthodes disponibles

| Méthode | Description |
|---------|-------------|
| `add_request(...)` | Enregistre une nouvelle requête |
| `get_consolidated_stats()` | Statistiques consolidées par jour |
| `get_daily_stats(date)` | Détails pour une journée spécifique |
| `get_total_usage()` | Utilisation totale de tokens |
| `get_requests_by_model(model)` | Filtre les requêtes par modèle |
| `export_to_csv(filename)` | Exporte les données en CSV |
| `clear_data()` | Efface toutes les données |

## 📁 Structure des données

Les données sont stockées dans un fichier JSON avec cette structure :

```json
{
  "requests": [
    {
      "timestamp": "2024-01-15T10:30:00.123456",
      "request_name": "Analyse de texte",
      "prompt_tokens": 50,
      "completion_tokens": 150,
      "total_tokens": 200,
      "model": "mistral-tiny",
      "temperature": 0.7,
      "metadata": {}
    }
  ],
  "consolidated": {
    "2024-01-15": {
      "total_prompt_tokens": 150,
      "total_completion_tokens": 230,
      "total_tokens": 380,
      "request_count": 2,
      "models": {"mistral-tiny": 1, "mistral-small": 1},
      "requests": ["Analyse de texte", "Traduction FR->EN"]
    }
  }
}
```

## 🎯 Cas d'usage

### Suivi des coûts
```python
# Coût par token (exemple pour Mistral)
COST_PER_PROMPT_TOKEN = 0.000002  # $0.000002 par token
COST_PER_COMPLETION_TOKEN = 0.000006  # $0.000006 par token

total = tracker.get_total_usage()
cost = (total['total_prompt_tokens'] * COST_PER_PROMPT_TOKEN + 
        total['total_completion_tokens'] * COST_PER_COMPLETION_TOKEN)
print(f"Coût total estimé : ${cost:.4f}")
```

### Visualisation avec Matplotlib
```python
import matplotlib.pyplot as plt

df = tracker.get_consolidated_stats()
plt.figure(figsize=(10, 5))
plt.bar(df['date'], df['total_tokens'])
plt.title('Utilisation quotidienne des tokens')
plt.xlabel('Date')
plt.ylabel('Tokens totaux')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## 🔧 Dépendances

- **Obligatoire** : Python 3.7+
- **Optionnel** : `pandas` pour les fonctionnalités DataFrame (recommandé)

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](../LICENSE) pour plus de détails.
