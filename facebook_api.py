# facebook_api.py
from generic_api import WebhookAPI

# Crée une instance de l'API pour Facebook
api = WebhookAPI(platform='facebook')

def post_update(title, text, image_path_or_url):
    return api.post_update(title, text, image_path_or_url)
