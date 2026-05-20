"""
Configuration centrale du système multi-agents universitaire.
Toutes les constantes et paramètres sont définis ici pour faciliter la maintenance.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env
load_dotenv()

# ── Chemins du projet ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"        # Documents source
CHROMA_DB_DIR = DATA_DIR / "chroma_db" # Index vectoriel ChromaDB

# ── Configuration Ollama (LLM local) ──────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
# nomic-embed-text : modèle d'embedding open-source de haute qualité
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# ── Configuration ChromaDB ─────────────────────────────────────────────────────
COLLECTION_NAME = "university_assistant"

# ── Paramètres RAG ────────────────────────────────────────────────────────────
# Chunk size = 512 tokens : bon équilibre entre contexte et précision sémantique
CHUNK_SIZE = 512
# Overlap = 50 tokens : évite de couper les informations à cheval entre deux chunks
CHUNK_OVERLAP = 50
# Top-K = 5 : nombre de passages pertinents récupérés par requête
TOP_K = 5

# ── Paramètres Agents ─────────────────────────────────────────────────────────
# Nombre maximum de re-tentatives si la validation échoue
MAX_VALIDATION_RETRIES = 2
