"""
Token Tracker Package

Un outil simple pour suivre et consolider l'utilisation des tokens
par requête pour les modèles de langage.

Utilisation :
    from token_tracker import TokenTracker
    
    tracker = TokenTracker("mon_suivi.json")
    tracker.add_request("Ma requête", prompt_tokens=50, completion_tokens=150)
    print(tracker.get_total_usage())
"""

from .token_tracker import TokenTracker

__version__ = "1.0.0"
__all__ = ["TokenTracker"]
