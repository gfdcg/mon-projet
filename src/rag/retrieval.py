"""
Module de retrieval : interrogation sémantique de la base de connaissances.

Ce module expose la fonction principale retrieve_context() utilisée
par les outils LangChain des agents.

Recherche : similarité cosinus Top-K=5 dans ChromaDB via LlamaIndex.
"""
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL, TOP_K
from src.rag.indexing import load_index

# ── Singleton : évite de recharger l'index à chaque requête ───────────────────
_query_engine = None


def get_query_engine() -> RetrieverQueryEngine:
    """
    Retourne le query engine LlamaIndex (pattern Singleton).

    Configuration :
    - LLM : Ollama/mistral (synthèse des passages récupérés)
    - Retriever : similarité cosinus, Top-K=5
    - Timeout : 120s (pour les modèles Ollama locaux qui peuvent être lents)
    """
    global _query_engine
    if _query_engine is None:
        index = load_index()
        llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            request_timeout=120.0,
        )
        _query_engine = index.as_query_engine(
            llm=llm,
            similarity_top_k=TOP_K,
            streaming=False,
            response_mode="compact",
        )
    return _query_engine


def retrieve_context(query: str) -> str:
    """
    Effectue une recherche sémantique et retourne les passages pertinents.

    Processus :
        1. La requête est convertie en vecteur (nomic-embed-text)
        2. Recherche des TOP_K chunks les plus proches dans ChromaDB
        3. LlamaIndex synthétise les passages en une réponse cohérente

    Args:
        query: La question ou requête en langage naturel.

    Returns:
        Contexte pertinent extrait des documents universitaires,
        avec indication des sources (nom du fichier + score de similarité).
    """
    engine = get_query_engine()
    response = engine.query(query)

    # Construction de la réponse avec traçabilité des sources
    context_text = str(response)

    sources = []
    if hasattr(response, "source_nodes") and response.source_nodes:
        for node in response.source_nodes[:TOP_K]:
            filename = node.metadata.get("file_name", "source inconnue")
            score = getattr(node, "score", None)
            score_str = f"{score:.3f}" if score is not None else "N/A"
            sources.append(f"  • {filename} (similarité: {score_str})")

    if sources:
        context_text += "\n\n📚 Sources consultées:\n" + "\n".join(sources)

    return context_text


def reset_query_engine() -> None:
    """Réinitialise le singleton (utile après une ré-indexation)."""
    global _query_engine
    _query_engine = None
