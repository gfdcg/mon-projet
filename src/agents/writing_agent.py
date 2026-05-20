"""
Agent 3 — Rédaction : Formule une réponse claire et structurée pour l'étudiant.

Raisonnement : Prompt structuré via LCEL
- Produit une réponse adaptée au niveau universitaire
- Structure la réponse avec des sections claires
- Prend en compte le feedback de l'Agent Validation si disponible
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# ── Prompt de l'Agent Rédaction ───────────────────────────────────────────────
WRITING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es l'Agent Rédaction d'un Assistant Universitaire Intelligent.

Ta MISSION : rédiger une réponse claire, complète et bien structurée pour un étudiant universitaire.

DIRECTIVES DE RÉDACTION :
✅ Utilise un langage clair et accessible aux étudiants
✅ Structure ta réponse avec des sections (titres, listes à puces)
✅ Cite les sources (ex: "Selon le règlement intérieur...", "D'après le guide étudiant...")
✅ Sois précis sur les dates, conditions et procédures
✅ Propose des étapes concrètes si la question concerne une procédure
✅ Termine par un résumé ou conseil pratique si approprié
✅ Réponds toujours en FRANÇAIS

Si tu reçois un feedback de l'Agent Validation, intègre-le pour améliorer ta réponse."""),

    ("human", """Question de l'étudiant : {question}

Analyse préparée par l'Agent Analyse :
{analysis}

Feedback de l'Agent Validation (si présent) :
{feedback}

Rédige maintenant une réponse complète et structurée pour l'étudiant."""),
])


def run_writing(question: str, analysis: str, feedback: str = "") -> str:
    """
    Rédige la réponse finale destinée à l'étudiant.

    Temperature=0.4 : plus élevée que les autres agents pour permettre
    une rédaction fluide et naturelle tout en restant factuel.

    Args:
        question: La question originale de l'étudiant.
        analysis: L'analyse structurée produite par l'Agent Analyse.
        feedback: Le retour critique de l'Agent Validation (vide si 1ère itération).

    Returns:
        Réponse rédigée et formatée pour l'étudiant.
    """
    iteration = "révision" if feedback else "1ère rédaction"
    print(f"\n[Agent Rédaction] ✍️ Rédaction en cours ({iteration})...")

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.4,
    )

    chain = WRITING_PROMPT | llm | StrOutputParser()

    result = chain.invoke({
        "question": question,
        "analysis": analysis,
        "feedback": feedback if feedback else "Aucun feedback (première rédaction).",
    })

    print("[Agent Rédaction] ✅ Réponse rédigée.")
    return result
