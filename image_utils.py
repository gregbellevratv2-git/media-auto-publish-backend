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

    # --- Redimensionnement final (Max 1280px sur le plus grand côté) ---
    max_dimension = 1280
    width, height = combined_image.size
    
    if width > max_dimension or height > max_dimension:
        if width > height:
            # Paysage : on fixe la largeur à 1280
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            # Portrait ou Carré : on fixe la hauteur à 1280
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
            
        final_image = combined_image.resize((new_width, new_height), Image.LANCZOS)
        print(f"Image redimensionnée à {new_width}x{new_height} (Max 1280px)")
    else:
        final_image = combined_image
        print(f"Image conservée à {width}x{height} (<= 1280px)")

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
