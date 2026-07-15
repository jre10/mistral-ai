"""
Token Tracker - Outil pour enregistrer et consolider l'utilisation des tokens
par requête pour les modèles de langage (Mistral AI, OpenAI, etc.).

Utilisation dans Jupyter Lab :
    from token_tracker import TokenTracker
    tracker = TokenTracker()
    tracker.add_request("Nom de la requête", prompt_tokens=50, completion_tokens=150)
"""

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class TokenTracker:
    """
    Classe pour suivre et enregistrer l'utilisation des tokens par requête.
    Consolide automatiquement les données et génère des statistiques.
    
    Exemple d'utilisation :
        tracker = TokenTracker("mon_suivi_tokens.json")
        tracker.add_request("Analyse de texte", prompt_tokens=50, 
                           completion_tokens=150, model="mistral-tiny")
        df_stats = tracker.get_consolidated_stats()
    """

    def __init__(self, storage_file="token_usage.json"):
        """
        Initialise le tracker avec un fichier de stockage.

        Args:
            storage_file (str): Chemin vers le fichier JSON de stockage.
                               Par défaut : "token_usage.json" dans le répertoire courant.
        """
        self.storage_file = Path(storage_file)
        self.usage_data = self._load_data()

    def _load_data(self):
        """Charge les données existantes depuis le fichier."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des données : {e}")
                return {"requests": [], "consolidated": {}}
        return {"requests": [], "consolidated": {}}

    def _save_data(self):
        """Sauvegarde les données dans le fichier."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def add_request(self, request_name, prompt_tokens, completion_tokens, total_tokens=None,
                   model=None, temperature=None, metadata=None):
        """
        Enregistre une nouvelle requête.

        Args:
            request_name (str): Nom ou identifiant de la requête
            prompt_tokens (int): Nombre de tokens dans le prompt
            completion_tokens (int): Nombre de tokens dans la réponse
            total_tokens (int, optional): Total des tokens (prompt + completion).
                                         Si None, calculé automatiquement.
            model (str, optional): Modèle utilisé (ex: "mistral-tiny", "mistral-small")
            temperature (float, optional): Température utilisée pour la génération
            metadata (dict, optional): Métadonnées supplémentaires à enregistrer

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
            "metadata": metadata or {}
        }

        self.usage_data["requests"].append(request_record)
        self._update_consolidated(request_record)
        self._save_data()

        return request_record

    def _update_consolidated(self, request_record):
        """Met à jour les données consolidées par jour."""
        date_key = datetime.fromisoformat(request_record["timestamp"]).strftime("%Y-%m-%d")
        
        if date_key not in self.usage_data["consolidated"]:
            self.usage_data["consolidated"][date_key] = {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "request_count": 0,
                "models": defaultdict(int),
                "requests": []
            }

        consolidated = self.usage_data["consolidated"][date_key]
        consolidated["total_prompt_tokens"] += request_record["prompt_tokens"]
        consolidated["total_completion_tokens"] += request_record["completion_tokens"]
        consolidated["total_tokens"] += request_record["total_tokens"]
        consolidated["request_count"] += 1
        consolidated["models"][request_record["model"]] += 1
        consolidated["requests"].append(request_record["request_name"])

    def get_consolidated_stats(self, as_dataframe=True):
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
                    data.append({
                        "date": date,
                        "total_prompt_tokens": stats["total_prompt_tokens"],
                        "total_completion_tokens": stats["total_completion_tokens"],
                        "total_tokens": stats["total_tokens"],
                        "request_count": stats["request_count"],
                        "models": models_str
                    })
                return pd.DataFrame(data)
            except ImportError:
                pass
        
        return dict(self.usage_data["consolidated"])

    def get_daily_stats(self, date=None, as_dataframe=True):
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
                        "timestamp": req["timestamp"]
                    }
                    for req in self.usage_data["requests"]
                    if datetime.fromisoformat(req["timestamp"]).strftime("%Y-%m-%d") == date
                ]
                return pd.DataFrame(data)
            except ImportError:
                pass
        
        return dict(self.usage_data["consolidated"][date])

    def get_total_usage(self):
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

    def get_requests_by_model(self, model_name, as_dataframe=True):
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

    def clear_data(self):
        """Efface toutes les données enregistrées."""
        self.usage_data = {"requests": [], "consolidated": {}}
        self._save_data()

    def export_to_csv(self, filename="token_usage.csv"):
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

    def __repr__(self):
        total = self.get_total_usage()
        return (f"TokenTracker(\n"
                f"  total_prompt_tokens={total['total_prompt_tokens']},\n"
                f"  total_completion_tokens={total['total_completion_tokens']},\n"
                f"  total_tokens={total['total_tokens']},\n"
                f"  request_count={total['request_count']}\n"
                f")")
