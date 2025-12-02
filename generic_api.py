import requests
from typing import Optional
from config import settings

class WebhookAPI:
    def __init__(self, platform: str):
        self.platform = platform
        self.webhook_url = self._get_webhook_url(platform)
        
        print(f"Initialisation du client API pour {self.platform.capitalize()} (via Webhook)...")
        if not self.webhook_url:
             print(f"ATTENTION : L'URL du webhook pour {self.platform.capitalize()} n'est pas configurée !")

    def _get_webhook_url(self, platform: str) -> str:
        if platform == 'linkedin':
            return settings.LINKEDIN_WEBHOOK_URL
        elif platform == 'instagram':
            return settings.INSTAGRAM_WEBHOOK_URL
        elif platform == 'facebook':
            return settings.FACEBOOK_WEBHOOK_URL
        return ""

    def post_update(self, title: Optional[str], text: str, image_path_or_url: Optional[str] = None) -> tuple[bool, str]:
        print("-" * 20)
        print(f"Préparation de l'envoi au webhook pour publication sur {self.platform.capitalize()}...")
        
        image_url = None
        if image_path_or_url:
            if image_path_or_url.startswith(('http://', 'https://')):
                image_url = image_path_or_url
                print(f"URL d'image valide détectée : {image_url}")
            else:
                print(f"Avertissement : Le chemin de fichier local '{image_path_or_url}' ne peut pas être envoyé.")

        full_text = text
        if title:
            full_text = f"{title}\n\n{text}"

        payload = {
            "title": title,
            "text": full_text,
            "image_url": image_url 
        }
        
        # LOGGING DEBUG
        print(f"DEBUG PAYLOAD ({self.platform}): {payload}")

        if not self.webhook_url:
             return False, f"URL Webhook non configurée pour {self.platform}"

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=15)
            
            # LOGGING RESPONSE
            print(f"DEBUG RESPONSE STATUS: {response.status_code}")
            print(f"DEBUG RESPONSE BODY: {response.text}")

            # Make.com retourne souvent "Accepted" ou juste 200 OK
            if response.status_code >= 200 and response.status_code < 300:
                message = f"Webhook pour {self.platform.capitalize()} reçu avec succès par Make.com."
                print(f">>> SUCCÈS : {message}")
                return True, message
            else:
                message = f"Erreur du webhook pour {self.platform.capitalize()} : Status {response.status_code} - {response.text}"
                print(f">>> ÉCHEC : {message}")
                return False, message
        except requests.exceptions.RequestException as e:
            message = f"Erreur de connexion au webhook pour {self.platform.capitalize()} : {e}"
            print(f">>> ÉCHEC CRITIQUE : {message}")
            return False, message
