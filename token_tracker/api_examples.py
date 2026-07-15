"""
Exemples d'intégration avec les API (Mistral, OpenAI, etc.)

Ce fichier montre comment utiliser le TokenTracker avec différentes API.
Copiez-collez ces exemples dans votre code ou Jupyter Lab.
"""

from token_tracker import TokenTracker

# Initialisation du tracker
tracker = TokenTracker("api_token_usage.json")

# ============================================================================
# EXEMPLE 1: Avec l'API Mistral (mistralai/mistral-src)
# ============================================================================

def example_mistral_api():
    """
    Exemple d'utilisation avec l'API Mistral.
    
    Installation requise:
        pip install mistralai
    """
    try:
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        
        # Initialiser le client Mistral
        client = MistralClient(api_key="votre_api_key_mistral")
        
        # Exemple 1: Enregistrement manuel après appel API
        messages = [
            ChatMessage(role="user", content="Quelle est la capitale de la France ?")
        ]
        
        # Appel API
        response = client.chat(
            model="mistral-tiny",
            messages=messages,
            temperature=0.7
        )
        
        # Enregistrer la réponse avec détection automatique des tokens
        tracker.add_mistral_response(
            request_name="Q: Capitale de la France",
            response=response.model_dump(),  # ou response.dict() selon la version
            model="mistral-tiny",
            temperature=0.7,
            metadata={"category": "géographie"}
        )
        
        # Exemple 2: Utilisation avec le wrapper (recommandé)
        # Le wrapper enregistre automatiquement la requête
        def mistral_chat_with_tracking(model, messages, request_name, temperature=0.7, **kwargs):
            """Wrapper pour chat Mistral avec suivi automatique des tokens."""
            response = client.chat(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            
            # Enregistrer automatiquement
            tracker.add_mistral_response(
                request_name=request_name,
                response=response.model_dump(),
                model=model,
                temperature=temperature,
                metadata=kwargs.get("metadata", {})
            )
            
            return response
        
        # Utilisation du wrapper
        response = mistral_chat_with_tracking(
            model="mistral-small",
            messages=[ChatMessage(role="user", content="Explique la photosynthèse")],
            request_name="Explication photosynthèse",
            temperature=0.3,
            metadata={"subject": "biologie", "priority": "high"}
        )
        
        print("✅ Exemple Mistral API terminé")
        
    except ImportError:
        print("⚠️  Le package 'mistralai' n'est pas installé.")
        print("   Installez-le avec: pip install mistralai")


# ============================================================================
# EXEMPLE 2: Avec l'API OpenAI
# ============================================================================

def example_openai_api():
    """
    Exemple d'utilisation avec l'API OpenAI.
    
    Installation requise:
        pip install openai
    """
    try:
        from openai import OpenAI
        
        # Initialiser le client OpenAI
        client = OpenAI(api_key="votre_api_key_openai")
        
        # Exemple 1: Enregistrement manuel après appel API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, how are you?"}
            ],
            temperature=0.7
        )
        
        # Enregistrer la réponse avec détection automatique des tokens
        tracker.add_openai_response(
            request_name="Q: Hello",
            response=response.model_dump(),  # ou response.dict()
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Exemple 2: Wrapper pour OpenAI avec suivi automatique
        def openai_chat_with_tracking(model, messages, request_name, temperature=0.7, **kwargs):
            """Wrapper pour chat OpenAI avec suivi automatique des tokens."""
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            
            # Enregistrer automatiquement
            tracker.add_openai_response(
                request_name=request_name,
                response=response.model_dump(),
                model=model,
                temperature=temperature,
                metadata=kwargs.get("metadata", {})
            )
            
            return response
        
        # Utilisation du wrapper
        response = openai_chat_with_tracking(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Write a poem about AI"}],
            request_name="Poème sur l'IA",
            temperature=0.8,
            metadata={"type": "creative", "language": "english"}
        )
        
        print("✅ Exemple OpenAI API terminé")
        
    except ImportError:
        print("⚠️  Le package 'openai' n'est pas installé.")
        print("   Installez-le avec: pip install openai")


# ============================================================================
# EXEMPLE 3: Avec l'API Hugging Face
# ============================================================================

def example_huggingface_api():
    """
    Exemple d'utilisation avec l'API Hugging Face Inference.
    
    Installation requise:
        pip install huggingface_hub
    """
    try:
        from huggingface_hub import InferenceClient
        
        # Initialiser le client
        client = InferenceClient(token="votre_api_key_huggingface")
        
        # Exemple avec modèle Hugging Face
        response = client.chat(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {"role": "user", "content": "What is machine learning?"}
            ],
            temperature=0.7
        )
        
        # Pour Hugging Face, les tokens ne sont pas toujours dans la réponse
        # On peut les estimer ou les calculer manuellement
        # Ici on utilise la méthode générique avec estimation
        
        # Estimation des tokens (simplifiée)
        prompt_text = "What is machine learning?"
        completion_text = str(response)
        
        # Estimation très basique (1 token ≈ 4 caractères)
        prompt_tokens = len(prompt_text) // 4
        completion_tokens = len(completion_text) // 4
        
        tracker.add_request(
            request_name="Q: What is ML?",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            temperature=0.7,
            metadata={
                "source": "huggingface_api",
                "response_length": len(completion_text)
            }
        )
        
        print("✅ Exemple Hugging Face API terminé")
        
    except ImportError:
        print("⚠️  Le package 'huggingface_hub' n'est pas installé.")
        print("   Installez-le avec: pip install huggingface_hub")


# ============================================================================
# EXEMPLE 4: Avec l'API Anthropic
# ============================================================================

def example_anthropic_api():
    """
    Exemple d'utilisation avec l'API Anthropic.
    
    Installation requise:
        pip install anthropic
    """
    try:
        from anthropic import Anthropic
        
        # Initialiser le client
        client = Anthropic(api_key="votre_api_key_anthropic")
        
        # Exemple avec Claude
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello, Claude!"}
            ]
        )
        
        # Anthropic retourne les tokens dans usage
        response_dict = message.model_dump()
        
        tracker.add_generic_response(
            request_name="Q: Hello Claude",
            response=response_dict,
            prompt_key="input_tokens",  # Anthropic utilise input_tokens au lieu de prompt_tokens
            completion_key="output_tokens",
            model="claude-3-sonnet-20240229",
            metadata={"source": "anthropic_api"}
        )
        
        print("✅ Exemple Anthropic API terminé")
        
    except ImportError:
        print("⚠️  Le package 'anthropic' n'est pas installé.")
        print("   Installez-le avec: pip install anthropic")


# ============================================================================
# EXEMPLE 5: Wrapper universel pour n'importe quelle API
# ============================================================================

def create_api_wrapper(tracker, api_name: str = "custom"):
    """
    Crée un wrapper universel pour n'importe quelle API.
    
    Args:
        tracker: Instance de TokenTracker
        api_name: Nom de l'API pour le suivi
    
    Returns:
        Fonction wrapper qui enregistre automatiquement les requêtes
    """
    def api_wrapper(func):
        """Décorateur pour envelopper les appels API."""
        def wrapper(*args, **kwargs):
            # Appel de la fonction originale
            result = func(*args, **kwargs)
            
            # Extraction des paramètres
            request_name = kwargs.get("request_name", "unnamed_request")
            model = kwargs.get("model", kwargs.get("model_name", "unknown"))
            temperature = kwargs.get("temperature", None)
            
            # Si la réponse contient des tokens
            if isinstance(result, dict) and "usage" in result:
                tracker.add_generic_response(
                    request_name=request_name,
                    response=result,
                    model=model,
                    temperature=temperature,
                    metadata={"api": api_name, **kwargs.get("metadata", {})}
                )
            else:
                # Sinon, enregistrement manuel nécessaire
                print(f"⚠️  Impossible d'extraire les tokens automatiquement pour {api_name}")
                print("   Utilisez tracker.add_request() manuellement")
            
            return result
        return wrapper
    return api_wrapper


# ============================================================================
# EXEMPLE 6: Calcul de coût avec différentes API
# ============================================================================

def calculate_api_costs():
    """
    Calcule le coût total basé sur les tokens utilisés et les tarifs des API.
    """
    # Tarifs (à mettre à jour selon les prix actuels)
    PRICING = {
        # Mistral
        "mistral-tiny": {"prompt": 0.000002, "completion": 0.000006},
        "mistral-small": {"prompt": 0.000002, "completion": 0.000006},
        "mistral-medium": {"prompt": 0.000007, "completion": 0.000027},
        "mistral-large": {"prompt": 0.000015, "completion": 0.000045},
        
        # OpenAI
        "gpt-3.5-turbo": {"prompt": 0.0000015, "completion": 0.000002},
        "gpt-4": {"prompt": 0.00003, "completion": 0.00006},
        "gpt-4-turbo": {"prompt": 0.00001, "completion": 0.00003},
        
        # Anthropic
        "claude-3-sonnet": {"prompt": 0.000003, "completion": 0.000015},
        "claude-3-haiku": {"prompt": 0.00000025, "completion": 0.00000125},
        "claude-3-opus": {"prompt": 0.000015, "completion": 0.000075},
    }
    
    total_cost = 0
    costs_by_model = {}
    
    for req in tracker.usage_data["requests"]:
        model = req.get("model", "unknown")
        
        if model in PRICING:
            pricing = PRICING[model]
            cost = (req["prompt_tokens"] * pricing["prompt"] + 
                   req["completion_tokens"] * pricing["completion"])
            total_cost += cost
            
            if model not in costs_by_model:
                costs_by_model[model] = 0
            costs_by_model[model] += cost
    
    print("=" * 50)
    print("COÛTS ESTIMÉS PAR MODÈLE")
    print("=" * 50)
    for model, cost in costs_by_model.items():
        print(f"{model}: ${cost:.6f}")
    print("-" * 50)
    print(f"COÛT TOTAL: ${total_cost:.6f}")
    print("=" * 50)
    
    return {"total": total_cost, "by_model": costs_by_model}


# ============================================================================
# EXEMPLE 7: Utilisation complète avec toutes les fonctionnalités
# ============================================================================

def full_example():
    """
    Exemple complet montrant toutes les fonctionnalités.
    """
    print("\n" + "="*60)
    print("EXEMPLE COMPLET D'UTILISATION")
    print("="*60)
    
    # 1. Enregistrement manuel
    print("\n1. Enregistrement manuel...")
    tracker.add_request(
        request_name="Test manuel",
        prompt_tokens=10,
        completion_tokens=20,
        model="test-model",
        metadata={"type": "test"}
    )
    
    # 2. Simulation de réponses API
    print("2. Simulation de réponses API...")
    
    # Simulation réponse Mistral
    mock_mistral_response = {
        "outputs": [{"text": "La capitale de la France est Paris.", "stop_reason": "end"}],
        "usage": {
            "prompt_tokens": 8,
            "completion_tokens": 12,
            "total_tokens": 20
        },
        "model": "mistral-tiny"
    }
    tracker.add_mistral_response(
        request_name="Mock: Capitale France",
        response=mock_mistral_response,
        temperature=0.7
    )
    
    # Simulation réponse OpenAI
    mock_openai_response = {
        "choices": [{"message": {"content": "Hello! How can I help you?"}}],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 25,
            "total_tokens": 40
        },
        "model": "gpt-3.5-turbo"
    }
    tracker.add_openai_response(
        request_name="Mock: Hello",
        response=mock_openai_response,
        temperature=0.8
    )
    
    # 3. Afficher les statistiques
    print("\n3. Statistiques consolidées:")
    print(tracker.get_consolidated_stats(as_dataframe=False))
    
    print("\n4. Utilisation totale:")
    print(tracker.get_total_usage())
    
    print("\n5. Requêtes par source:")
    for source in ["manual", "mistral_api", "openai_api"]:
        reqs = tracker.get_requests_by_source(source, as_dataframe=False)
        print(f"  {source}: {len(reqs)} requêtes")
    
    print("\n6. Calcul des coûts:")
    calculate_api_costs()
    
    print("\n7. Export CSV...")
    tracker.export_to_csv("exemple_token_usage.csv")
    print("   ✅ Export terminé")
    
    print("\n" + "="*60)
    print("EXEMPLE TERMINÉ")
    print("="*60)


# ============================================================================
# EXÉCUTION DES EXEMPLES
# ============================================================================

if __name__ == "__main__":
    print("Token Tracker - Exemples d'intégration API")
    print("=" * 50)
    
    # Exécuter l'exemple complet (sans dépendances externes)
    full_example()
    
    print("\n\nPour tester avec de vraies API, décommentez les lignes suivantes :")
    print("# example_mistral_api()")
    print("# example_openai_api()")
    print("# example_huggingface_api()")
    print("# example_anthropic_api()")
