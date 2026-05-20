"""
Script d'ingestion : charge les documents et construit l'index ChromaDB.

Ce script doit être lancé UNE SEULE FOIS (ou à chaque ajout de nouveaux documents).
L'index est persisté sur disque dans data/chroma_db/.

Usage : python scripts/ingest.py
        python scripts/ingest.py --force  (force la ré-indexation)
"""
import sys
import argparse
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.ingestion import load_documents, split_documents
from src.rag.indexing import build_index, index_exists
from src.rag.retrieval import reset_query_engine


def main():
    parser = argparse.ArgumentParser(description="Ingestion RAG des documents universitaires")
    parser.add_argument("--force", action="store_true",
                        help="Force la ré-indexation même si un index existe")
    args = parser.parse_args()

    print("=" * 60)
    print("  Pipeline d'Ingestion RAG — Assistant Universitaire")
    print("=" * 60)

    # Vérification si l'index existe déjà
    if index_exists() and not args.force:
        print("\n✅ Un index ChromaDB existe déjà.")
        print("   Utilisez --force pour forcer la ré-indexation.")
        print("   → Le système est prêt ! Lancez : python main.py")
        return

    # Étape 1 : Chargement des documents
    print("\n📂 Étape 1/3 — Chargement des documents...")
    documents = load_documents()

    # Étape 2 : Découpage en chunks
    print("\n✂️  Étape 2/3 — Découpage en chunks...")
    nodes = split_documents(documents)

    # Étape 3 : Indexation dans ChromaDB
    print("\n🔢 Étape 3/3 — Génération des embeddings et indexation...")
    build_index(nodes)

    # Réinitialisation du singleton de retrieval
    reset_query_engine()

    print("\n" + "=" * 60)
    print("✅ Ingestion terminée avec succès !")
    print("   → Lancez maintenant : python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
