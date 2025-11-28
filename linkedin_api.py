# linkedin_api.py
from generic_api import WebhookAPI

# Crée une instance de l'API pour LinkedIn
api = WebhookAPI(platform='linkedin')

def post_update(title, text, image_path_or_url):
    return api.post_update(title, text, image_path_or_url)
