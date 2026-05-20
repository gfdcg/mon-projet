"""
Outils LangChain wrappant le pipeline RAG LlamaIndex.

Ces tools sont utilisés par les agents LangChain. Chaque tool est une
fonction Python décorée qui effectue une recherche sémantique dans
la base de connaissances universitaire.

Architecture du bridge LangChain ↔ LlamaIndex :
    Agent LangChain → Tool LangChain → retrieve_context() → LlamaIndex → ChromaDB
"""
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from src.rag.retrieval import retrieve_context


# ── Schémas d'entrée Pydantic ─────────────────────────────────────────────────

class RAGSearchInput(BaseModel):
    """Schéma de validation pour la recherche RAG."""
    query: str = Field(
        description=(
            "La question ou requête à rechercher dans la base de connaissances "
            "universitaire (règlement, cours, procédures, calendrier, FAQ...)."
        )
    )


# ── Fonctions sous-jacentes ───────────────────────────────────────────────────

def _search_university_knowledge(query: str) -> str:
    """Recherche principale dans la base de connaissances universitaire."""
    try:
        result = retrieve_context(query)
        return result if result.strip() else "Aucune information trouvée pour cette requête."
    except Exception as e:
        return f"Erreur lors de la recherche RAG : {str(e)}"


def _search_regulations(query: str) -> str:
    """Recherche spécialisée dans les règlements et procédures."""
    try:
        enriched = f"règlement procédure officielle : {query}"
        return retrieve_context(enriched)
    except Exception as e:
        return f"Erreur : {str(e)}"


def _search_courses(query: str) -> str:
    """Recherche spécialisée dans le catalogue des cours et syllabus."""
    try:
        enriched = f"cours syllabus programme enseignement : {query}"
        return retrieve_context(enriched)
    except Exception as e:
        return f"Erreur : {str(e)}"


# ── Tools LangChain ───────────────────────────────────────────────────────────

rag_search_tool = StructuredTool.from_function(
    func=_search_university_knowledge,
    name="recherche_base_universitaire",
    description=(
        "Recherche des informations dans la base de connaissances universitaire. "
        "Utilise cet outil pour toute question sur : les cours, le règlement intérieur, "
        "les procédures administratives (inscriptions, équivalences, transferts), "
        "le calendrier académique, les examens, les absences, la scolarité."
    ),
    args_schema=RAGSearchInput,
)

regulations_tool = StructuredTool.from_function(
    func=_search_regulations,
    name="recherche_reglements",
    description=(
        "Recherche spécialisée dans les règlements et procédures officielles de l'université. "
        "Préférer cet outil pour les questions sur : règles d'assiduité, conditions de passage, "
        "sanctions disciplinaires, droits des étudiants."
    ),
    args_schema=RAGSearchInput,
)

courses_tool = StructuredTool.from_function(
    func=_search_courses,
    name="recherche_cours_syllabus",
    description=(
        "Recherche spécialisée dans le catalogue des cours et les syllabus. "
        "Préférer cet outil pour les questions sur : contenu d'un cours, crédits ECTS, "
        "prérequis, modalités d'évaluation, enseignants."
    ),
    args_schema=RAGSearchInput,
)

# Liste complète des outils disponibles pour les agents
ALL_TOOLS = [rag_search_tool, regulations_tool, courses_tool]
