"""
Module d'indexation : génération des embeddings et stockage dans ChromaDB.

Pipeline :
    Chunks → Embeddings (nomic-embed-text via Ollama) → ChromaDB (persisté)

Le vector store ChromaDB est persisté sur disque dans data/chroma_db/
afin d'éviter de re-indexer à chaque démarrage.
"""
from typing import List

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import BaseNode
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    CHROMA_DB_DIR,
    COLLECTION_NAME,
)


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Retourne un client ChromaDB persisté sur disque.

    Le répertoire data/chroma_db/ est créé automatiquement si absent.
    La persistance permet de ne pas re-indexer à chaque démarrage.
    """
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DB_DIR))


def get_embedding_model() -> OllamaEmbedding:
    """
    Retourne le modèle d'embedding Ollama.

    Modèle choisi : nomic-embed-text
    - Open-source et gratuit via Ollama
    - 768 dimensions — bonne représentation sémantique
    - Optimisé pour la recherche de passages textuels
    """
    return OllamaEmbedding(
        model_name=OLLAMA_EMBED_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def build_index(nodes: List[BaseNode]) -> VectorStoreIndex:
    """
    Construit et persiste l'index vectoriel à partir des chunks.

    Pipeline d'indexation :
        1. Chaque chunk → vecteur (768 dims) via nomic-embed-text
        2. Les vecteurs sont stockés dans la collection ChromaDB
        3. L'index LlamaIndex wrappe ChromaDB pour les requêtes

    Args:
        nodes: Chunks issus de ingestion.split_documents()

    Returns:
        VectorStoreIndex prêt pour les requêtes sémantiques.
    """
    embed_model = get_embedding_model()
    chroma_client = get_chroma_client()

    # Récupération ou création de la collection ChromaDB
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print(f"[Indexation] ⏳ Génération des embeddings ({OLLAMA_EMBED_MODEL})...")
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    count = collection.count()
    print(f"[Indexation] ✅ {count} vecteurs stockés dans ChromaDB ({CHROMA_DB_DIR})")
    return index


def load_index() -> VectorStoreIndex:
    """
    Charge l'index existant depuis ChromaDB sans re-indexer.

    À utiliser lors du démarrage normal du système (après une première ingestion).
    Beaucoup plus rapide que build_index() car les embeddings sont déjà calculés.

    Returns:
        VectorStoreIndex chargé depuis ChromaDB.
    """
    embed_model = get_embedding_model()
    chroma_client = get_chroma_client()

    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    count = collection.count()
    print(f"[Indexation] ✅ Index chargé — {count} vecteurs dans ChromaDB")
    return index


def index_exists() -> bool:
    """Vérifie si un index ChromaDB existe déjà (évite la ré-indexation)."""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)
        return collection.count() > 0
    except Exception:
        return False
