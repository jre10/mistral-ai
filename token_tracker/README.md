# Token Tracker 📊

Un outil Python simple pour **enregistrer, suivre et consolider** l'utilisation des tokens par requête pour les modèles de langage (Mistral AI, OpenAI, Anthropic, etc.).

Parfait pour **Jupyter Lab** - il suffit de copier-coller et d'utiliser !

## ✨ Fonctionnalités

- 📝 **Enregistrement des requêtes** : Stocke chaque requête avec ses métadonnées
- 🤖 **Intégration API** : Détection automatique des tokens depuis les réponses API
- 📊 **Consolidation automatique** : Statistiques par jour, par modèle, par source
- 💾 **Persistance** : Sauvegarde dans un fichier JSON
- 📈 **Analyse** : Statistiques détaillées et totaux
- 💰 **Calcul de coût** : Estimation des coûts par modèle
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

# Installer les dépendances optionnelles
pip install pandas matplotlib mistralai openai
```

## 💡 Utilisation

### Méthode 1 : Enregistrement manuel (basique)

```python
from token_tracker import TokenTracker

# Créer un tracker (crée un fichier token_usage.json)
tracker = TokenTracker()

# Enregistrer une requête manuellement
tracker.add_request(
    request_name="Analyse de texte",
    prompt_tokens=50,
    completion_tokens=150,
    model="mistral-tiny",
    temperature=0.7
)
```

### Méthode 2 : Avec réponse API Mistral (automatique)

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from token_tracker import TokenTracker

# Initialiser
client = MistralClient(api_key="votre_api_key")
tracker = TokenTracker()

# Appel API
response = client.chat(
    model="mistral-tiny",
    messages=[ChatMessage(role="user", content="Quelle est la capitale de la France ?")]
)

# Enregistrer avec détection automatique des tokens
tracker.add_mistral_response(
    request_name="Q: Capitale France",
    response=response.model_dump(),
    model="mistral-tiny"
)
```

### Méthode 3 : Avec réponse API OpenAI (automatique)

```python
from openai import OpenAI
from token_tracker import TokenTracker

# Initialiser
client = OpenAI(api_key="votre_api_key")
tracker = TokenTracker()

# Appel API
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Enregistrer avec détection automatique des tokens
tracker.add_openai_response(
    request_name="Q: Hello",
    response=response.model_dump(),
    model="gpt-3.5-turbo"
)
```

### Méthode 4 : Avec n'importe quelle API (générique)

```python
from token_tracker import TokenTracker

# Pour les API qui utilisent des noms de clés différents
tracker = TokenTracker()

response = {
    "usage": {
        "input_tokens": 25,      # Au lieu de prompt_tokens
        "output_tokens": 15      # Au lieu de completion_tokens
    },
    "model": "claude-3-sonnet"
}

tracker.add_generic_response(
    request_name="Requête Claude",
    response=response,
    prompt_key="input_tokens",      # Clé personnalisée pour prompt
    completion_key="output_tokens", # Clé personnalisée pour completion
    model="claude-3-sonnet"
)
```

## 📋 Méthodes disponibles

### Enregistrement
| Méthode | Description | Source |
|---------|-------------|--------|
| `add_request(...)` | Enregistrement manuel | `manual` |
| `add_mistral_response(...)` | Depuis réponse API Mistral | `mistral_api` |
| `add_openai_response(...)` | Depuis réponse API OpenAI | `openai_api` |
| `add_generic_response(...)` | Depuis n'importe quelle API | `generic_api` |

### Statistiques
| Méthode | Description |
|---------|-------------|
| `get_consolidated_stats()` | Statistiques consolidées par jour |
| `get_daily_stats(date)` | Détails pour une journée spécifique |
| `get_total_usage()` | Utilisation totale de tokens |
| `get_requests_by_model(model)` | Filtre les requêtes par modèle |
| `get_requests_by_source(source)` | Filtre les requêtes par source API |

### Export
| Méthode | Description |
|---------|-------------|
| `export_to_csv(filename)` | Exporte les données en CSV |
| `clear_data()` | Efface toutes les données |

## 🎯 Intégration avec les API

### API Supportées

| API | Méthode | Package requis | Installation |
|-----|---------|----------------|--------------|
| **Mistral** | `add_mistral_response()` | `mistralai` | `pip install mistralai` |
| **OpenAI** | `add_openai_response()` | `openai` | `pip install openai` |
| **Anthropic** | `add_generic_response()` | `anthropic` | `pip install anthropic` |
| **Hugging Face** | `add_generic_response()` | `huggingface_hub` | `pip install huggingface_hub` |
| **Autre** | `add_generic_response()` | - | - |

### Exemple de Wrapper pour Mistral

```python
from mistralai.client import MistralClient
from token_tracker import TokenTracker

client = MistralClient(api_key="votre_api_key")
tracker = TokenTracker()

def mistral_chat_with_tracking(model, messages, request_name, **kwargs):
    """Wrapper qui enregistre automatiquement les tokens."""
    response = client.chat(model=model, messages=messages, **kwargs)
    
    # Enregistrement automatique
    tracker.add_mistral_response(
        request_name=request_name,
        response=response.model_dump(),
        model=model,
        metadata=kwargs.get("metadata", {})
    )
    
    return response

# Utilisation
response = mistral_chat_with_tracking(
    model="mistral-small",
    messages=[ChatMessage(role="user", content="Explique l'IA")],
    request_name="Explication IA",
    temperature=0.3
)
```

### Exemple de Wrapper pour OpenAI

```python
from openai import OpenAI
from token_tracker import TokenTracker

client = OpenAI(api_key="votre_api_key")
tracker = TokenTracker()

def openai_chat_with_tracking(model, messages, request_name, **kwargs):
    """Wrapper qui enregistre automatiquement les tokens."""
    response = client.chat.completions.create(
        model=model, 
        messages=messages, 
        **kwargs
    )
    
    tracker.add_openai_response(
        request_name=request_name,
        response=response.model_dump(),
        model=model,
        metadata=kwargs.get("metadata", {})
    )
    
    return response

# Utilisation
response = openai_chat_with_tracking(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Write a poem"}],
    request_name="Poème",
    temperature=0.8
)
```

## 💰 Calcul de coût

```python
# Tarifs (à mettre à jour selon les prix actuels)
PRICING = {
    "mistral-tiny": {"prompt": 0.000002, "completion": 0.000006},
    "mistral-small": {"prompt": 0.000002, "completion": 0.000006},
    "gpt-3.5-turbo": {"prompt": 0.0000015, "completion": 0.000002},
    "gpt-4": {"prompt": 0.00003, "completion": 0.00006},
}

total_cost = 0
for req in tracker.usage_data["requests"]:
    model = req.get("model", "unknown")
    if model in PRICING:
        pricing = PRICING[model]
        cost = (req["prompt_tokens"] * pricing["prompt"] + 
               req["completion_tokens"] * pricing["completion"])
        total_cost += cost

print(f"Coût total estimé : ${total_cost:.6f}")
```

Voir [`api_examples.py`](api_examples.py) pour une implémentation complète du calcul de coût.

## 📊 Visualisation

```python
import matplotlib.pyplot as plt

# Graphique d'utilisation quotidienne
df = tracker.get_consolidated_stats()
plt.figure(figsize=(12, 6))
plt.bar(df['date'], df['total_tokens'], color='skyblue')
plt.title('Utilisation quotidienne des tokens')
plt.xlabel('Date')
plt.ylabel('Tokens totaux')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Camembert par modèle
df_models = tracker.get_consolidated_stats()
# ... (code pour créer un camembert)
```

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
      "metadata": {"category": "analyse"},
      "source": "manual"
    },
    {
      "timestamp": "2024-01-15T10:31:00.456789",
      "request_name": "Q: Capitale France",
      "prompt_tokens": 25,
      "completion_tokens": 10,
      "total_tokens": 35,
      "model": "mistral-tiny",
      "temperature": 0.7,
      "metadata": {},
      "source": "mistral_api",
      "response_preview": "La capitale de la France est Paris..."
    }
  ],
  "consolidated": {
    "2024-01-15": {
      "total_prompt_tokens": 75,
      "total_completion_tokens": 160,
      "total_tokens": 235,
      "request_count": 2,
      "models": {"mistral-tiny": 2},
      "sources": {"manual": 1, "mistral_api": 1},
      "requests": ["Analyse de texte", "Q: Capitale France"]
    }
  }
}
```

## 🎓 Bonnes pratiques

### 1. Utilisez des wrappers
Créez des wrappers pour vos appels API pour un enregistrement automatique :

```python
def my_mistral_chat(messages, request_name, **kwargs):
    response = client.chat(messages=messages, **kwargs)
    tracker.add_mistral_response(request_name, response.model_dump(), **kwargs)
    return response
```

### 2. Ajoutez des métadonnées
Utilisez le paramètre `metadata` pour ajouter du contexte :

```python
tracker.add_mistral_response(
    request_name="Analyse document",
    response=response,
    metadata={
        "project": "projet_x",
        "user": "john",
        "priority": "high"
    }
)
```

### 3. Sauvegardez régulièrement
Le tracker sauvegarde automatiquement après chaque ajout, mais vous pouvez forcer une sauvegarde :

```python
tracker._save_data()  # Sauvegarde manuelle
```

### 4. Utilisez plusieurs trackers
Créez des trackers séparés pour différents projets :

```python
# Tracker pour le projet A
project_a_tracker = TokenTracker("projet_a_tokens.json")

# Tracker pour le projet B
project_b_tracker = TokenTracker("projet_b_tokens.json")
```

## 🔧 Dépendances

- **Obligatoire** : Python 3.7+
- **Optionnel** : 
  - `pandas` pour les fonctionnalités DataFrame
  - `matplotlib` pour la visualisation
  - `mistralai` pour l'intégration Mistral
  - `openai` pour l'intégration OpenAI

## 📚 Fichiers inclus

| Fichier | Description |
|---------|-------------|
| `token_tracker.py` | Code principal de la classe TokenTracker |
| `__init__.py` | Initialisation du package |
| `api_examples.py` | Exemples d'intégration avec différentes API |
| `example_notebook.ipynb` | Notebook Jupyter avec exemples complets |
| `requirements.txt` | Dépendances optionnelles |
| `README.md` | Documentation (ce fichier) |

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](../LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou une pull request sur [GitHub](https://github.com/jre10/mistral-ai).
