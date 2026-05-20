"""
Agent 1 — Recherche : Interroge la base de connaissances via RAG.

Raisonnement : Multi-query LCEL pipeline
- Effectue plusieurs recherches parallèles sur la base de connaissances
- Synthétise les résultats en une réponse structurée via le LLM
- Compatible avec LangChain v1.x (pas d'AgentExecutor requis)
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.tools.rag_tool import (
    _search_university_knowledge,
    _search_regulations,
    _search_courses,
)

# ── Prompt de synthèse des résultats RAG ─────────────────────────────────────
RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es l'Agent Recherche d'un Assistant Universitaire Intelligent.

Ta MISSION : compiler et organiser les informations extraites de la base de \
connaissances universitaire pour répondre à la question posée.

Tu reçois les résultats bruts de trois recherches parallèles :
1. Recherche générale dans la base universitaire
2. Recherche dans les règlements et procédures officielles
3. Recherche dans le catalogue des cours et syllabus

Tu dois :
- Fusionner les informations pertinentes en éliminant les doublons
- Garder les faits clés : dates, conditions, étapes, règles, chiffres
- Indiquer la source de chaque information si disponible
- Signaler si les informations sont insuffisantes

IMPORTANT : Tu fournis uniquement les informations brutes extraites et synthétisées.
Tu ne rédiges PAS la réponse finale destinée à l'étudiant."""),

    ("human", """Question : {question}

--- Résultat 1 : Recherche générale ---
{result_general}

--- Résultat 2 : Règlements et procédures ---
{result_regulations}

--- Résultat 3 : Cours et syllabus ---
{result_courses}

Compile ces informations en une synthèse structurée et pertinente."""),
])


def run_research(question: str) -> str:
    """
    Exécute l'Agent Recherche sur une question donnée.

    Stratégie multi-requêtes :
    - Interroge les trois outils RAG en parallèle (général, règlements, cours)
    - Synthétise les résultats via un LLM (LCEL chain)
    - Fallback sur une recherche directe en cas d'échec du LLM

    Args:
        question: La question originale de l'étudiant.

    Returns:
        Passages pertinents extraits et synthétisés depuis la base de connaissances.
    """
    print("\n[Agent Recherche] 🔍 Démarrage des recherches parallèles...")

    # ── Étape 1 : Interrogation des trois outils RAG ──────────────────────────
    try:
        result_general     = _search_university_knowledge(question)
        result_regulations = _search_regulations(question)
        result_courses     = _search_courses(question)
        print("[Agent Recherche] ✅ Recherches RAG terminées.")
    except Exception as e:
        print(f"[Agent Recherche] ⚠️ Erreur RAG ({e}), fallback direct...")
        from src.rag.retrieval import retrieve_context
        return retrieve_context(question)

    # ── Étape 2 : Synthèse via LLM (LCEL) ────────────────────────────────────
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )
        chain = RESEARCH_PROMPT | llm | StrOutputParser()
        output = chain.invoke({
            "question":           question,
            "result_general":     result_general,
            "result_regulations": result_regulations,
            "result_courses":     result_courses,
        })
        print("[Agent Recherche] ✅ Synthèse complète.")
        return output
    except Exception as e:
        print(f"[Agent Recherche] ⚠️ Synthèse LLM échouée ({e}), retour brut...")
        # Fallback : concaténation brute des trois recherches
        parts = [
            f"[Recherche générale]\n{result_general}",
            f"[Règlements]\n{result_regulations}",
            f"[Cours]\n{result_courses}",
        ]
        return "\n\n".join(p for p in parts if "Aucune" not in p and p.strip())
