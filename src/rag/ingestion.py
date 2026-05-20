"""
Module d'ingestion des documents universitaires.

Responsable du chargement et du découpage (chunking) des documents
avant leur indexation dans ChromaDB.

Pipeline :
    Documents (PDF/TXT/JSON) → Chargement → Chunks → [indexation.py]
"""
from pathlib import Path
from typing import List

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, BaseNode

from src.config import RAW_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_documents() -> List[Document]:
    """
    Charge tous les documents depuis le répertoire data/raw/.

    Formats supportés : PDF, TXT, JSON, CSV

    Returns:
        Liste de Documents LlamaIndex prêts pour le chunking.

    Raises:
        FileNotFoundError: Si le répertoire data/raw/ n'existe pas.
    """
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Répertoire introuvable : {RAW_DATA_DIR}\n"
            "Lancez d'abord : python scripts/generate_data.py"
        )

    reader = SimpleDirectoryReader(
        input_dir=str(RAW_DATA_DIR),
        recursive=True,
        required_exts=[".pdf", ".txt", ".json"],
    )

    documents = reader.load_data()
    print(f"[Ingestion] ✅ {len(documents)} documents chargés depuis {RAW_DATA_DIR}")
    return documents


def split_documents(documents: List[Document]) -> List[BaseNode]:
    """
    Découpe les documents en chunks sémantiques.

    Stratégie de chunking choisie :
    - SentenceSplitter : respecte les frontières de phrases (meilleure cohérence)
    - Taille : 512 tokens — équilibre entre contexte riche et précision sémantique
    - Overlap : 50 tokens — évite de perdre des informations à cheval entre chunks

    Args:
        documents: Liste de Documents LlamaIndex.

    Returns:
        Liste de nœuds (chunks) prêts pour l'embedding.
    """
    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    nodes = splitter.get_nodes_from_documents(documents)
    print(
        f"[Ingestion] ✅ {len(nodes)} chunks créés "
        f"(taille={CHUNK_SIZE} tokens, overlap={CHUNK_OVERLAP} tokens)"
    )
    return nodes
