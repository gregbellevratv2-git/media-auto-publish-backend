from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from scheduler_service import start_scheduler, scheduler
from routers import auth, posts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Démarrage de l'application...")
    init_db()
    start_scheduler()
    yield
    # Shutdown
    print("Arrêt de l'application...")
    if scheduler.running:
        scheduler.shutdown()

app = FastAPI(
    title="Media Auto Publish API",
    description="API pour la planification et la publication automatique de posts sur les réseaux sociaux.",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
from fastapi.middleware.cors import CORSMiddleware

# Liste des origines autorisées (les domaines de votre frontend)
origins = [
    "http://localhost:3000",  # Pour le développement local React
    "http://localhost:5173",  # Pour le développement local Vite
    "https://www.storage-gbphotos.ovh",  # Domaine OVH réel
    "https://storage-gbphotos.ovh",
    "https://www.gregbellevrat.fr", # Votre domaine OVH (Exemple)
    "https://gregbellevrat.fr",
    # Ajoutez ici l'URL exacte de votre site OVH une fois déployé
    "*" # A REMPLACER par les domaines spécifiques en production pour la sécurité
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Media Auto Publish"}
