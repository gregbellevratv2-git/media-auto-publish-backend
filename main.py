from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from scheduler_service import start_scheduler, scheduler
from routers import auth, posts
from migrations import run_migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Démarrage de l'application...")
    init_db()
    run_migrations() # Exécuter les migrations
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
    "https://www.storage-gbphotos.ovh",  # Domaine OVH frontend
    "https://storage-gbphotos.ovh",  # Domaine OVH sans www
    "https://www.gregbellevrat.fr",  # Autre domaine
    "https://gregbellevrat.fr",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Media Auto Publish"}
