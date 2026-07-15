"""
Token Tracker - Outil pour enregistrer et consolider l'utilisation des tokens
par requête pour les modèles de langage (Mistral AI, OpenAI, etc.).

Utilisation dans Jupyter Lab :
    from token_tracker import TokenTracker
    tracker = TokenTracker()
    
    # Méthode 1: Enregistrement manuel
    tracker.add_request("Nom de la requête", prompt_tokens=50, completion_tokens=150)
    
    # Méthode 2: Avec réponse API Mistral
    response = mistral_client.chat(...)
    tracker.add_mistral_response("Ma requête", response)
    
    # Méthode 3: Avec réponse API OpenAI
    response = openai_client.chat.completions.create(...)
    tracker.add_openai_response("Ma requête", response)
"""

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, Any, Union


class TokenTracker:
    """
    Classe pour suivre et enregistrer l'utilisation des tokens par requête.
    Consolide automatiquement les données et génère des statistiques.
    
    Supporte :
    - Enregistrement manuel des tokens
    - Détection automatique depuis les réponses API Mistral
    - Détection automatique depuis les réponses API OpenAI
    - Wrapper pour appels API avec enregistrement automatique
    
    Exemple d'utilisation :
        tracker = TokenTracker("mon_suivi_tokens.json")
        
        # Enregistrement manuel
        tracker.add_request("Analyse de texte", prompt_tokens=50, 
                           completion_tokens=150, model="mistral-tiny")
        
        # Depuis une réponse Mistral
        response = mistral_client.chat(model="mistral-tiny", messages=[...])
        tracker.add_mistral_response("Requête Mistral", response)
        
        # Depuis une réponse OpenAI
        response = openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=[...])
        tracker.add_openai_response("Requête OpenAI", response)
        
        # Obtenir des statistiques
        df_stats = tracker.get_consolidated_stats()
    """

    def __init__(self, storage_file: str = "token_usage.json"):
        """
        Initialise le tracker avec un fichier de stockage.

        Args:
            storage_file (str): Chemin vers le fichier JSON de stockage.
                               Par défaut : "token_usage.json" dans le répertoire courant.
        """
        self.storage_file = Path(storage_file)
        self.usage_data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Charge les données existantes depuis le fichier."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des données : {e}")
                return {"requests": [], "consolidated": {}}
        return {"requests": [], "consolidated": {}}

    def _save_data(self) -> None:
        """Sauvegarde les données dans le fichier."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def _extract_tokens_from_dict(self, data: Dict[str, Any], 
                                 prompt_key: str = "prompt_tokens", 
                                 completion_key: str = "completion_tokens") -> Dict[str, int]:
        """Extrait les tokens depuis un dictionnaire de réponse API."""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        
        # Recherche dans usage
        if "usage" in data:
            usage = data["usage"]
            if isinstance(usage, dict):
                prompt_tokens = usage.get(prompt_key, usage.get("prompt_token", 0))
                completion_tokens = usage.get(completion_key, usage.get("completion_token", 0))
                total_tokens = usage.get("total_tokens", usage.get("total_token", 0))
        
        # Recherche directe
        if prompt_tokens == 0:
            prompt_tokens = data.get(prompt_key, data.get("prompt_token", 0))
        if completion_tokens == 0:
            completion_tokens = data.get(completion_key, data.get("completion_token", 0))
        if total_tokens == 0:
            total_tokens = data.get("total_tokens", data.get("total_token", 0))
        
        # Calcul total si non fourni
        if total_tokens == 0 and prompt_tokens > 0 and completion_tokens > 0:
            total_tokens = prompt_tokens + completion_tokens
        
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens)
        }

    def add_request(self, request_name: str, prompt_tokens: int, completion_tokens: int, 
                   total_tokens: Optional[int] = None, model: Optional[str] = None,
                   temperature: Optional[float] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enregistre une nouvelle requête (méthode manuelle).

        Args:
            request_name (str): Nom ou identifiant de la requête
            prompt_tokens (int): Nombre de tokens dans le prompt
            completion_tokens (int): Nombre de tokens dans la réponse
            total_tokens (int, optional): Total des tokens (prompt + completion)
            model (str, optional): Modèle utilisé
            temperature (float, optional): Température utilisée
            metadata (dict, optional): Métadonnées supplémentaires

        Returns:
            dict: L'enregistrement de la requête ajoutée
        """
        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens

        request_record = {
            "timestamp": datetime.now().isoformat(),
            "request_name": request_name,
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "model": model,
            "temperature": temperature,
            "metadata": metadata or {},
            "source": "manual"
        }

        self.usage_data["requests"].append(request_record)
        self._update_consolidated(request_record)
        self._save_data()

        return request_record

    def add_mistral_response(self, request_name: str, response: Dict[str, Any],
                            model: Optional[str] = None, temperature: Optional[float] = None,
                            metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enregistre une requête depuis une réponse de l'API Mistral.
        
        Format attendu de la réponse :
        {
            "outputs": [...],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 10,
                "total_tokens": 35
            }
        }
        
        Args:
            request_name (str): Nom de la requête
            response (dict): Réponse complète de l'API Mistral
            model (str, optional): Modèle utilisé (peut être extrait de la réponse)
            temperature (float, optional): Température utilisée
            metadata (dict, optional): Métadonnées supplémentaires

        Returns:
            dict: L'enregistrement de la requête ajoutée
        """
        # Extraire le modèle depuis la réponse si non fourni
        if model is None and "model" in response:
            model = response["model"]
        
        # Extraire les tokens
        tokens = self._extract_tokens_from_dict(response, "prompt_tokens", "completion_tokens")
        
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "request_name": request_name,
            "prompt_tokens": tokens["prompt_tokens"],
            "completion_tokens": tokens["completion_tokens"],
            "total_tokens": tokens["total_tokens"],
            "model": model,
            "temperature": temperature,
            "metadata": metadata or {},
            "source": "mistral_api",
            "response_preview": str(response.get("outputs", [{}])[0].get("text", "")[:100]) if response.get("outputs") else ""
        }

        self.usage_data["requests"].append(request_record)
        self._update_consolidated(request_record)
        self._save_data()

        return request_record

    def add_openai_response(self, request_name: str, response: Dict[str, Any],
                           model: Optional[str] = None, temperature: Optional[float] = None,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enregistre une requête depuis une réponse de l'API OpenAI.
        
        Format attendu de la réponse :
        {
            "choices": [...],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 10,
                "total_tokens": 35
            }
        }
        
        Args:
            request_name (str): Nom de la requête
            response (dict): Réponse complète de l'API OpenAI
            model (str, optional): Modèle utilisé (peut être extrait de la réponse)
            temperature (float, optional): Température utilisée
            metadata (dict, optional): Métadonnées supplémentaires

        Returns:
            dict: L'enregistrement de la requête ajoutée
        """
        # Extraire le modèle depuis la réponse si non fourni
        if model is None and "model" in response:
            model = response["model"]
        
        # Extraire les tokens
        tokens = self._extract_tokens_from_dict(response, "prompt_tokens", "completion_tokens")
        
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "request_name": request_name,
            "prompt_tokens": tokens["prompt_tokens"],
            "completion_tokens": tokens["completion_tokens"],
            "total_tokens": tokens["total_tokens"],
            "model": model,
            "temperature": temperature,
            "metadata": metadata or {},
            "source": "openai_api",
            "response_preview": str(response.get("choices", [{}])[0].get("message", {}).get("content", "")[:100]) if response.get("choices") else ""
        }

        self.usage_data["requests"].append(request_record)
        self._update_consolidated(request_record)
        self._save_data()

        return request_record

    def add_generic_response(self, request_name: str, response: Dict[str, Any],
                           prompt_key: str = "prompt_tokens", 
                           completion_key: str = "completion_tokens",
                           model: Optional[str] = None, temperature: Optional[float] = None,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enregistre une requête depuis une réponse d'API générique.
        
        Permet de gérer n'importe quelle API qui retourne des tokens.
        
        Args:
            request_name (str): Nom de la requête
            response (dict): Réponse complète de l'API
            prompt_key (str): Clé pour les tokens du prompt (défaut: "prompt_tokens")
            completion_key (str): Clé pour les tokens de complétion (défaut: "completion_tokens")
            model (str, optional): Modèle utilisé
            temperature (float, optional): Température utilisée
            metadata (dict, optional): Métadonnées supplémentaires

        Returns:
            dict: L'enregistrement de la requête ajoutée
        """
        # Extraire les tokens avec les clés personnalisées
        tokens = self._extract_tokens_from_dict(response, prompt_key, completion_key)
        
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "request_name": request_name,
            "prompt_tokens": tokens["prompt_tokens"],
            "completion_tokens": tokens["completion_tokens"],
            "total_tokens": tokens["total_tokens"],
            "model": model,
            "temperature": temperature,
            "metadata": metadata or {},
            "source": "generic_api",
            "api_type": metadata.get("api_type", "unknown") if metadata else "unknown"
        }

        self.usage_data["requests"].append(request_record)
        self._update_consolidated(request_record)
        self._save_data()

        return request_record

    def _update_consolidated(self, request_record: Dict[str, Any]) -> None:
        """Met à jour les données consolidées par jour."""
        date_key = datetime.fromisoformat(request_record["timestamp"]).strftime("%Y-%m-%d")
        
        if date_key not in self.usage_data["consolidated"]:
            self.usage_data["consolidated"][date_key] = {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "request_count": 0,
                "models": defaultdict(int),
                "sources": defaultdict(int),
                "requests": []
            }

        consolidated = self.usage_data["consolidated"][date_key]
        consolidated["total_prompt_tokens"] += request_record["prompt_tokens"]
        consolidated["total_completion_tokens"] += request_record["completion_tokens"]
        consolidated["total_tokens"] += request_record["total_tokens"]
        consolidated["request_count"] += 1
        
        if request_record["model"]:
            consolidated["models"][request_record["model"]] += 1
        
        if request_record.get("source"):
            consolidated["sources"][request_record["source"]] += 1
            
        consolidated["requests"].append(request_record["request_name"])

    def get_consolidated_stats(self, as_dataframe: bool = True) -> Union[Any, Dict[str, Any]]:
        """
        Récupère les statistiques consolidées par jour.

        Args:
            as_dataframe (bool): Si True et si pandas est disponible,
                               retourne un DataFrame pandas.

        Returns:
            DataFrame ou dict: Statistiques consolidées
        """
        if as_dataframe:
            try:
                import pandas as pd
                data = []
                for date, stats in self.usage_data["consolidated"].items():
                    models_str = ", ".join([f"{k}({v})" for k, v in stats["models"].items()])
                    sources_str = ", ".join([f"{k}({v})" for k, v in stats.get("sources", {}).items()])
                    data.append({
                        "date": date,
                        "total_prompt_tokens": stats["total_prompt_tokens"],
                        "total_completion_tokens": stats["total_completion_tokens"],
                        "total_tokens": stats["total_tokens"],
                        "request_count": stats["request_count"],
                        "models": models_str,
                        "sources": sources_str
                    })
                return pd.DataFrame(data)
            except ImportError:
                pass
        
        return dict(self.usage_data["consolidated"])

    def get_daily_stats(self, date: Optional[str] = None, as_dataframe: bool = True) -> Union[Any, Dict[str, Any], None]:
        """
        Récupère les statistiques détaillées pour un jour spécifique.

        Args:
            date (str, optional): Date au format YYYY-MM-DD. 
                                Si None, utilise la date du jour.
            as_dataframe (bool): Si True et si pandas est disponible,
                               retourne un DataFrame pandas.

        Returns:
            DataFrame ou dict ou None: Statistiques pour le jour spécifié
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if date not in self.usage_data["consolidated"]:
            return None

        if as_dataframe:
            try:
                import pandas as pd
                data = [
                    {
                        "request_name": req["request_name"],
                        "prompt_tokens": req["prompt_tokens"],
                        "completion_tokens": req["completion_tokens"],
                        "total_tokens": req["total_tokens"],
                        "model": req["model"],
                        "temperature": req["temperature"],
                        "timestamp": req["timestamp"],
                        "source": req.get("source", "manual")
                    }
                    for req in self.usage_data["requests"]
                    if datetime.fromisoformat(req["timestamp"]).strftime("%Y-%m-%d") == date
                ]
                return pd.DataFrame(data)
            except ImportError:
                pass
        
        return dict(self.usage_data["consolidated"][date])

    def get_total_usage(self) -> Dict[str, int]:
        """
        Récupère l'utilisation totale de tokens sur toutes les périodes.

        Returns:
            dict: Utilisation totale avec les clés :
                 - total_prompt_tokens
                 - total_completion_tokens
                 - total_tokens
                 - request_count
        """
        total = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "request_count": 0
        }

        for stats in self.usage_data["consolidated"].values():
            total["total_prompt_tokens"] += stats["total_prompt_tokens"]
            total["total_completion_tokens"] += stats["total_completion_tokens"]
            total["total_tokens"] += stats["total_tokens"]
            total["request_count"] += stats["request_count"]

        return total

    def get_requests_by_model(self, model_name: str, as_dataframe: bool = True) -> Union[Any, list]:
        """
        Récupère toutes les requêtes pour un modèle spécifique.

        Args:
            model_name (str): Nom du modèle à filtrer
            as_dataframe (bool): Si True et si pandas est disponible,
                               retourne un DataFrame pandas.

        Returns:
            DataFrame ou list: Liste des requêtes pour le modèle spécifié
        """
        model_requests = [
            req for req in self.usage_data["requests"]
            if req["model"] == model_name
        ]

        if as_dataframe:
            try:
                import pandas as pd
                return pd.DataFrame(model_requests)
            except ImportError:
                pass
        
        return model_requests

    def get_requests_by_source(self, source: str, as_dataframe: bool = True) -> Union[Any, list]:
        """
        Récupère toutes les requêtes depuis une source spécifique (manual, mistral_api, openai_api).

        Args:
            source (str): Source à filtrer ("manual", "mistral_api", "openai_api", etc.)
            as_dataframe (bool): Si True et si pandas est disponible,
                               retourne un DataFrame pandas.

        Returns:
            DataFrame ou list: Liste des requêtes pour la source spécifiée
        """
        source_requests = [
            req for req in self.usage_data["requests"]
            if req.get("source") == source
        ]

        if as_dataframe:
            try:
                import pandas as pd
                return pd.DataFrame(source_requests)
            except ImportError:
                pass
        
        return source_requests

    def clear_data(self) -> None:
        """Efface toutes les données enregistrées."""
        self.usage_data = {"requests": [], "consolidated": {}}
        self._save_data()

    def export_to_csv(self, filename: str = "token_usage.csv") -> bool:
        """
        Exporte toutes les requêtes au format CSV.

        Args:
            filename (str): Nom du fichier CSV de sortie
        """
        try:
            import pandas as pd
            df = pd.DataFrame(self.usage_data["requests"])
            df.to_csv(filename, index=False)
            return True
        except ImportError:
            print("Pandas n'est pas installé. Impossible d'exporter en CSV.")
            return False

    def __repr__(self) -> str:
        total = self.get_total_usage()
        return (f"TokenTracker(\n"
                f"  total_prompt_tokens={total['total_prompt_tokens']},\n"
                f"  total_completion_tokens={total['total_completion_tokens']},\n"
                f"  total_tokens={total['total_tokens']},\n"
                f"  request_count={total['request_count']}\n"
                f")")
