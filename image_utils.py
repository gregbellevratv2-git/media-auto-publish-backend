import io
from PIL import Image
import cloudinary
import cloudinary.uploader
from config import settings

# --- Constantes ---
FINAL_IMAGE_HEIGHT = 1980
SPACE_BETWEEN_IMAGES = 50  # Espace en pixels entre les images

# --- Configuration Cloudinary ---
# Cloudinary est configuré automatiquement via la variable d'environnement CLOUDINARY_URL
# ou on peut le configurer manuellement si besoin, mais CLOUDINARY_URL est le standard.

def combine_and_resize_images(image_paths: list[str], platform: str) -> io.BytesIO | None:
    """
    Combine jusqu'à 3 images verticalement, les redimensionne et retourne un objet BytesIO.
    Prend en compte les contraintes spécifiques à la plateforme.
    """
    if not image_paths:
        return None

    # Note: image_paths ici peuvent être des chemins locaux (pour le dev) ou des objets file-like
    # Dans le contexte d'une API, on recevra probablement des bytes directement.
    # Pour l'instant, on suppose que ce sont des fichiers ouverts ou des chemins.
    
    images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            images.append(img)
        except Exception as e:
            print(f"Erreur lors de l'ouverture de l'image {path}: {e}")
            continue

    if not images:
        return None
    
    # --- Redimensionnement proportionnel initial ---
    base_width = images[0].width
    resized_images = [images[0]]
    for img in images[1:]:
        if img.width != base_width:
            aspect_ratio = img.height / img.width
            new_height = int(aspect_ratio * base_width)
            resized_images.append(img.resize((base_width, new_height), Image.LANCZOS))
        else:
            resized_images.append(img)

    # --- Création de l'image combinée ---
    total_height = sum(img.height for img in resized_images) + SPACE_BETWEEN_IMAGES * (len(resized_images) - 1)
    combined_image = Image.new('RGB', (base_width, total_height), 'white')

    current_y = 0
    for img in resized_images:
        combined_image.paste(img, (0, current_y))
        current_y += img.height + SPACE_BETWEEN_IMAGES

    # --- Redimensionnement final à la hauteur désirée ---
    final_aspect_ratio = combined_image.width / combined_image.height
    final_width = int(FINAL_IMAGE_HEIGHT * final_aspect_ratio)
    final_image = combined_image.resize((final_width, FINAL_IMAGE_HEIGHT), Image.LANCZOS)

    # --- Redimensionnement spécifique à Instagram ---
    if platform == 'instagram' and final_image.width > 1400:
        print(f"Image pour Instagram trop large ({final_image.width}px). Redimensionnement à 1400px de large.")
        insta_aspect_ratio = final_image.height / final_image.width
        new_height = int(1400 * insta_aspect_ratio)
        final_image = final_image.resize((1400, new_height), Image.LANCZOS)

    # --- Sauvegarde en mémoire ---
    output = io.BytesIO()
    final_image.save(output, format='JPEG', quality=90)
    output.seek(0)
    return output

def upload_image_to_cloudinary(image_data: io.BytesIO, folder: str = "media_auto_publish") -> str | None:
    """
    Télécharge une image sur Cloudinary et retourne l'URL sécurisée.
    """
    try:
        # Upload sur Cloudinary
        # resource_type="image" est par défaut
        response = cloudinary.uploader.upload(image_data, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        print(f"Erreur lors de l'upload Cloudinary: {e}")
        return None
