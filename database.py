from sqlmodel import SQLModel, create_engine, Session
from config import settings

# Use the DATABASE_URL from settings
# Ensure we are using the correct driver for psycopg2 if needed (postgresql+psycopg2://...)
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

# Fix for some postgres connection strings starting with postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    from models import User, Post  # Import models to register them
    SQLModel.metadata.create_all(engine)
