"""
Agent 4 — Validation : Vérifie la qualité et la pertinence de la réponse rédigée.

Raisonnement : Critique structurée via LCEL
- Évalue la pertinence par rapport à la question
- Vérifie la cohérence et l'exactitude des informations
- Retourne un verdict (valide/invalide) + feedback d'amélioration
- Déclenche une boucle de révision si la qualité est insuffisante
"""
import json
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# ── Prompt de l'Agent Validation ─────────────────────────────────────────────
VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es l'Agent Validation d'un Assistant Universitaire Intelligent.

Ta MISSION : évaluer objectivement la qualité de la réponse rédigée par l'Agent Rédaction.

CRITÈRES D'ÉVALUATION :
1. Pertinence (0-25pts) : La réponse répond-elle directement à la question ?
2. Exactitude (0-25pts) : Les informations sont-elles correctes et cohérentes avec les sources ?
3. Complétude (0-25pts) : Tous les aspects importants sont-ils couverts ?
4. Clarté (0-25pts) : La réponse est-elle bien structurée et compréhensible ?

RÈGLE DE VALIDATION : La réponse est VALIDE si le score total >= 70/100.

Tu DOIS répondre avec ce JSON exact :
{{
  "score": <nombre entre 0 et 100>,
  "is_valid": <true ou false>,
  "verdict": "<VALIDÉE ou À RÉVISER>",
  "feedback": "<feedback détaillé pour améliorer la réponse si invalide, sinon 'Réponse satisfaisante.'>",
  "points_forts": "<ce qui est bien>",
  "points_amelioration": "<ce qui doit être amélioré>"
}}"""),

    ("human", """Question originale de l'étudiant : {question}

Réponse rédigée par l'Agent Rédaction :
{draft_response}

Informations de référence (contexte RAG) :
{retrieved_docs}

Évalue cette réponse selon les critères et retourne le JSON de validation."""),
])


def _parse_validation_result(text: str) -> dict:
    """
    Parse le résultat JSON de l'agent validation.
    Gère les cas où le LLM inclut du texte autour du JSON.
    """
    # Cherche un bloc JSON dans le texte
    json_match = re.search(r'\{[^{}]*"is_valid"[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback : cherche les mots-clés booléens
    is_valid = "true" in text.lower() and "is_valid" in text.lower()
    if "à réviser" in text.lower() or "invalide" in text.lower():
        is_valid = False

    return {
        "score": 80 if is_valid else 50,
        "is_valid": is_valid,
        "verdict": "VALIDÉE" if is_valid else "À RÉVISER",
        "feedback": text if not is_valid else "Réponse satisfaisante.",
        "points_forts": "Non parsé",
        "points_amelioration": "Non parsé",
    }


def run_validation(question: str, draft_response: str, retrieved_docs: str) -> dict:
    """
    Valide la réponse rédigée par l'Agent Rédaction.

    Temperature=0.1 : très faible pour une évaluation objective et cohérente.

    Args:
        question: La question originale de l'étudiant.
        draft_response: La réponse produite par l'Agent Rédaction.
        retrieved_docs: Le contexte RAG pour vérifier l'exactitude.

    Returns:
        Dictionnaire avec :
        - is_valid (bool): True si la réponse est acceptée
        - score (int): Score sur 100
        - verdict (str): "VALIDÉE" ou "À RÉVISER"
        - feedback (str): Feedback pour l'Agent Rédaction si révision nécessaire
    """
    print("\n[Agent Validation] 🔎 Évaluation de la réponse en cours...")

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )

    chain = VALIDATION_PROMPT | llm | StrOutputParser()

    raw_result = chain.invoke({
        "question": question,
        "draft_response": draft_response,
        "retrieved_docs": retrieved_docs[:3000],  # Limite pour éviter overflow
    })

    result = _parse_validation_result(raw_result)

    verdict_icon = "✅" if result["is_valid"] else "❌"
    print(
        f"[Agent Validation] {verdict_icon} Score: {result['score']}/100 "
        f"— {result['verdict']}"
    )

    return result
