from sqlalchemy import text
from database import engine

def run_migrations():
    print("Vérification des migrations...")
    with engine.connect() as connection:
        try:
            # Vérifier si la colonne image_path existe
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='posts' AND column_name='image_path'"
            ))
            if result.fetchone():
                print("Migration: Renommage de image_path vers image_url...")
                connection.execute(text("ALTER TABLE posts RENAME COLUMN image_path TO image_url"))
                connection.commit()
                print("Migration terminée.")
            else:
                print("Aucune migration nécessaire (colonne image_path non trouvée).")
        except Exception as e:
            print(f"Erreur lors de la migration: {e}")
            # On ne bloque pas le démarrage si la migration échoue (peut-être déjà faite ou autre DB)
