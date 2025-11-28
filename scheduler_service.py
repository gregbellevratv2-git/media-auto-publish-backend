from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlmodel import Session, select
from database import engine, get_session
from models import Post
from datetime import datetime
import linkedin_api
import instagram_api
import facebook_api

# --- Import des modules API pour chaque plateforme ---
API_CLIENTS = {
    'linkedin': linkedin_api,
    'instagram': instagram_api,
    'facebook': facebook_api,
}

# --- Configuration du JobStore avec Postgres ---
jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}

scheduler = BackgroundScheduler(jobstores=jobstores)

def publish_post_task(post_id: int):
    print(f"Tâche déclenchée : Publication du post ID {post_id}")
    
    # On utilise une nouvelle session pour interagir avec la DB dans le thread du scheduler
    with Session(engine) as session:
        post = session.get(Post, post_id)
        
        if not post:
            print(f"Erreur : Post ID {post_id} non trouvé.")
            return
        if post.status != 'scheduled':
            print(f"Avertissement : Le post ID {post_id} n'est pas à l'état 'scheduled'. Tâche ignorée.")
            return

        platform = post.platform
        api_client = API_CLIENTS.get(platform)

        if not api_client:
            print(f"Erreur critique : Aucun client API trouvé pour la plateforme '{platform}'.")
            post.status = 'failed'
            post.error_message = f"Plateforme '{platform}' non supportée."
            session.add(post)
            session.commit()
            return

        try:
            # Passer le titre, le texte et l'image à la méthode post_update du bon client
            success, message = api_client.post_update(
                post.title, 
                post.text_content, 
                post.image_url # On utilise image_url maintenant
            )
            
            if success:
                post.status = 'published'
            else:
                post.status = 'failed'
                post.error_message = message
            
            session.add(post)
            session.commit()
                
        except Exception as e:
            print(f"Erreur critique lors de la publication du post ID {post_id} sur {platform}: {e}")
            post.status = 'failed'
            post.error_message = str(e)
            session.add(post)
            session.commit()

def schedule_new_post(post_id: int, scheduled_at: datetime):
    # On ajoute le job au scheduler
    # Note: replace_existing=True permet de mettre à jour si l'ID existe déjà
    scheduler.add_job(
        publish_post_task,
        'date',
        run_date=scheduled_at,
        args=[post_id],
        id=f'post_{post_id}',
        replace_existing=True
    )
    print(f"Post ID {post_id} programmé pour {scheduled_at}")

def remove_scheduled_post(post_id: int):
    job_id = f'post_{post_id}'
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"Tâche pour le post ID {post_id} supprimée du scheduler.")

def reschedule_post(post_id: int, new_scheduled_at: datetime):
    """Reprogramme un job existant pour une nouvelle date/heure."""
    job_id = f'post_{post_id}'
    if scheduler.get_job(job_id):
        scheduler.reschedule_job(job_id, trigger='date', run_date=new_scheduled_at)
        print(f"Post ID {post_id} reprogrammé pour {new_scheduled_at}")
    else:
        schedule_new_post(post_id, new_scheduled_at)

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("Scheduler démarré.")

def send_post_now_manual(post_id: int, session: Session) -> tuple[bool, str]:
    """
    Force l'envoi immédiat d'un post.
    Retourne un tuple (succès, message).
    """
    print(f"Envoi manuel forcé pour le post ID {post_id}")
    post = session.get(Post, post_id)
    
    if not post:
        return False, f"Post ID {post_id} non trouvé."

    platform = post.platform
    api_client = API_CLIENTS.get(platform)

    if not api_client:
        post.status = 'failed'
        post.error_message = f"Plateforme '{platform}' non supportée."
        session.add(post)
        session.commit()
        return False, f"Aucun client API trouvé pour la plateforme '{platform}'."

    try:
        success, message = api_client.post_update(
            post.title, 
            post.text_content, 
            post.image_url
        )
        
        if success:
            if post.status == 'scheduled':
                remove_scheduled_post(post_id)
            post.status = 'published'
        else:
            post.status = 'failed'
            post.error_message = message
        
        session.add(post)
        session.commit()
        
        return success, message
            
    except Exception as e:
        print(f"Erreur critique lors de l'envoi manuel du post ID {post_id} sur {platform}: {e}")
        post.status = 'failed'
        post.error_message = str(e)
        session.add(post)
        session.commit()
        return False, str(e)
