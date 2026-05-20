"""
Agent 2 — Analyse : Synthétise les informations extraites par l'Agent Recherche.

Raisonnement : Chain-of-thought via LCEL (LangChain Expression Language)
- Identifie les points clés pertinents pour la question
- Organise l'information de manière logique et hiérarchique
- Signale les informations manquantes ou incomplètes
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# ── Prompt de l'Agent Analyse ─────────────────────────────────────────────────
ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es l'Agent Analyse d'un Assistant Universitaire Intelligent.

Ta MISSION : analyser et synthétiser les informations brutes récupérées par l'Agent Recherche.

Tu dois produire une analyse structurée qui :
1. Identifie les informations DIRECTEMENT pertinentes pour la question posée
2. Organise les informations par ordre d'importance
3. Extrait les faits clés : dates, conditions, étapes, règles, nombres
4. Élimine les redondances et le bruit non pertinent
5. Signale les informations manquantes ou ambiguës
6. Prépare le terrain pour une réponse claire à l'étudiant

IMPORTANT : Tu ne rédiges PAS la réponse finale. Tu prépares une analyse
structurée qui sera utilisée par l'Agent Rédaction."""),

    ("human", """Question de l'étudiant : {question}

Informations brutes récupérées par l'Agent Recherche :
{retrieved_docs}

Effectue une analyse structurée en suivant cette structure :
## Points clés identifiés
## Faits importants (dates, conditions, règles)
## Informations manquantes ou incomplètes
## Synthèse pour la rédaction"""),
])


def run_analysis(question: str, retrieved_docs: str) -> str:
    """
    Analyse et synthétise les informations récupérées.

    Utilise une chaîne LCEL (LangChain Expression Language) :
        ANALYSIS_PROMPT | llm | StrOutputParser()

    Temperature=0.2 : légèrement supérieure à l'agent recherche
    pour permettre une analyse nuancée tout en restant factuel.

    Args:
        question: La question originale de l'étudiant.
        retrieved_docs: Les passages récupérés par l'Agent Recherche.

    Returns:
        Analyse structurée prête à être utilisée par l'Agent Rédaction.
    """
    print("\n[Agent Analyse] 🧠 Analyse des informations récupérées...")

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
    )

    # Chaîne LCEL : prompt → LLM → parser
    chain = ANALYSIS_PROMPT | llm | StrOutputParser()

    result = chain.invoke({
        "question": question,
        "retrieved_docs": retrieved_docs,
    })

    print("[Agent Analyse] ✅ Analyse complète.")
    return result
