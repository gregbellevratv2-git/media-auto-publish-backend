"""
Script Keep-Alive pour Media Auto Publish
==========================================

Ce script maintient le serveur actif et vérifie les publications en attente
toutes les 5 minutes en envoyant une requête HTTP.

NOUVEAU : Gestion des tranches horaires actives pour économiser les ressources.

Usage:
    python keep_alive.py

Configuration:
    - Modifiez SERVER_URL avec l'URL de votre serveur Render
    - Ajustez INTERVAL_MINUTES selon vos besoins (min 5 minutes recommandé)
    - Configurez ACTIVE_TIME_RANGES pour vos tranches horaires
"""

import requests
import time
from datetime import datetime, time as dt_time
import schedule

# ========== CONFIGURATION ==========
SERVER_URL = "https://votre-app.onrender.com"  # ← MODIFIEZ AVEC VOTRE URL RENDER
INTERVAL_MINUTES = 5  # Intervalle entre chaque vérification

# Tranches horaires actives (format 24h)
# Le script ne pingera le serveur QUE pendant ces périodes
ACTIVE_TIME_RANGES = [
    {"start": "09:00", "end": "10:00"},  # Matin : 9h-10h
    {"start": "17:00", "end": "18:00"},  # Soir : 17h-18h
]

# Si True, le script tournera 24/7
# Si False, il respectera les ACTIVE_TIME_RANGES
ALWAYS_ACTIVE = False
# ===================================


def is_in_active_time_range():
    """Vérifie si l'heure actuelle est dans une tranche horaire active."""
    if ALWAYS_ACTIVE:
        return True
    
    now = datetime.now().time()
    
    for time_range in ACTIVE_TIME_RANGES:
        start = datetime.strptime(time_range["start"], "%H:%M").time()
        end = datetime.strptime(time_range["end"], "%H:%M").time()
        
        if start <= now <= end:
            return True
    
    return False


def get_next_active_period():
    """Retourne la prochaine période d'activité (pour l'affichage)."""
    if ALWAYS_ACTIVE:
        return "Toujours actif (24/7)"
    
    now = datetime.now().time()
    
    for time_range in ACTIVE_TIME_RANGES:
        start = datetime.strptime(time_range["start"], "%H:%M").time()
        end = datetime.strptime(time_range["end"], "%H:%M").time()
        
        if now < start:
            return f"{time_range['start']} - {time_range['end']}"
    
    # Si on est après toutes les tranches, retourner la première de demain
    if ACTIVE_TIME_RANGES:
        return f"{ACTIVE_TIME_RANGES[0]['start']} - {ACTIVE_TIME_RANGES[0]['end']} (demain)"
    
    return "Aucune période configurée"


def ping_server():
    """Envoie une requête au serveur pour le maintenir éveillé et vérifier les posts en attente."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Vérifier si on est dans une tranche horaire active
    if not is_in_active_time_range():
        next_period = get_next_active_period()
        print(f"[{timestamp}] ⏸️  Hors période active - Prochaine: {next_period}")
        return
    
    try:
        # Vérifier les publications en attente
        response = requests.post(
            f"{SERVER_URL}/posts/check-pending-posts",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[{timestamp}] ✓ Serveur actif")
            print(f"  → Posts en attente vérifiés: {data['total_pending']}")
            print(f"  → Publiés: {data['published']} | Échecs: {data['failed']}")
            
            if data['details']:
                for detail in data['details']:
                    print(f"    {detail}")
        else:
            print(f"[{timestamp}] ⚠ Réponse inattendue: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"[{timestamp}] ✗ Erreur de connexion: {e}")
    except Exception as e:
        print(f"[{timestamp}] ✗ Erreur: {e}")


def main():
    """Lance le système de keep-alive."""
    print("=" * 60)
    print("  MEDIA AUTO PUBLISH - Keep Alive Service")
    print("=" * 60)
    print(f"Serveur cible: {SERVER_URL}")
    print(f"Intervalle: toutes les {INTERVAL_MINUTES} minutes")
    print(f"Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if ALWAYS_ACTIVE:
        print(f"Mode: ACTIF 24/7")
    else:
        print(f"Mode: TRANCHES HORAIRES")
        print(f"Périodes actives:")
        for time_range in ACTIVE_TIME_RANGES:
            print(f"  • {time_range['start']} - {time_range['end']}")
    
    print("=" * 60)
    print("\nAppuyez sur Ctrl+C pour arrêter\n")
    
    # Première exécution immédiate
    ping_server()
    
    # Planifier les exécutions suivantes
    schedule.every(INTERVAL_MINUTES).minutes.do(ping_server)
    
    # Boucle infinie
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[ARRÊT] Service Keep-Alive arrêté par l'utilisateur")


if __name__ == "__main__":
    main()
