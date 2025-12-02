"""
Script de Test - Validation Timezone UTC
==========================================

Ce script teste que le système de publication programmée fonctionne correctement
avec les nouveaux réglages UTC.

Il va:
1. Afficher l'heure actuelle en UTC et en heure locale
2. Montrer comment les dates doivent être formatées
3. Simuler une requête au endpoint /check-pending-posts

Usage:
    python test_timezone_fix.py
"""

from datetime import datetime, timedelta
import requests
import json

# ========== CONFIGURATION ==========
SERVER_URL = "https://media-auto-publish-backend.onrender.com"
# ===================================

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print_section("VALIDATION TIMEZONE UTC")
    
    # 1. Afficher les heures actuelles
    now_utc = datetime.utcnow()
    now_local = datetime.now()
    
    print(f"\n📅 Heure actuelle UTC     : {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"🕐 Heure actuelle locale  : {now_local.strftime('%Y-%m-%d %H:%M:%S')} (UTC+1)")
    print(f"⏰ Décalage               : {(now_local - now_utc).total_seconds() / 3600} heure(s)")
    
    # 2. Montrer comment formater une date pour l'envoi
    print_section("FORMAT D'ENVOI FRONTEND → BACKEND")
    
    scheduled_local = now_local + timedelta(minutes=5)
    print(f"\nVous programmez : {scheduled_local.strftime('%d/%m/%Y %H:%M')} (heure française)")
    print(f"↓")
    
    # JavaScript toISOString() équivalent en Python
    scheduled_utc = datetime.utcnow() + timedelta(minutes=5)
    iso_format = scheduled_utc.isoformat() + "Z"
    print(f"Frontend envoie : {iso_format}")
    print(f"↓")
    print(f"Backend stocke  : {scheduled_utc.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
    
    # 3. Test du endpoint
    print_section("TEST ENDPOINT /check-pending-posts")
    
    try:
        print(f"\n🔍 Interrogation du serveur : {SERVER_URL}")
        response = requests.post(
            f"{SERVER_URL}/posts/check-pending-posts",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Serveur opérationnel")
            print(f"   Posts en attente : {data['total_pending']}")
            print(f"   Publiés          : {data['published']}")
            print(f"   Échecs           : {data['failed']}")
            
            if data['details']:
                print(f"\n📝 Détails :")
                for detail in data['details']:
                    print(f"   {detail}")
        else:
            print(f"\n⚠️  Status HTTP: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erreur de connexion : {e}")
    
    # 4. Recommandations
    print_section("RECOMMANDATIONS")
    print("""
✅ CORRECTIF APPLIQUÉ:
   • Backend : Utilise datetime.utcnow() partout
   • Frontend: Envoie les dates avec toISOString() (format UTC)
   • Affichage: Conversion automatique UTC → heure locale

📋 POUR TESTER:
   1. Créez un post programmé pour dans 5 minutes via le frontend
   2. Vérifiez dans la console que la date est au format ISO (se termine par Z)
   3. Attendez 5 minutes avec keep_alive.py actif
   4. Le post devrait être automatiquement publié

⚠️  ATTENTION:
   • Tous les nouveaux posts seront en UTC
   • Les anciens posts peuvent avoir des dates ambiguës
   • Il est recommandé de reprogrammer les posts existants
    """)

if __name__ == "__main__":
    main()
