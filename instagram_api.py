# instagram_api.py
from generic_api import WebhookAPI

# Crée une instance de l'API pour Instagram
api = WebhookAPI(platform='instagram')

def post_update(title, text, image_path_or_url):
    return api.post_update(title, text, image_path_or_url)
