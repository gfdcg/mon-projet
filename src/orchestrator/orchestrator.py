"""
Orchestrateur principal — LangGraph StateGraph.

Coordonne les 4 agents via un flux séquentiel avec boucle de feedback :

    START → [research] → [analysis] → [writing] → [validation] → END
                                           ↑___________↓ (si révision)

L'état partagé (AgentState) transite de nœud en nœud et s'enrichit
à chaque étape. Le routage conditionnel après validation permet
de déclencher une révision si la qualité est insuffisante.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from src.agents.research_agent import run_research
from src.agents.analysis_agent import run_analysis
from src.agents.writing_agent import run_writing
from src.agents.validation_agent import run_validation
from src.config import MAX_VALIDATION_RETRIES


# ── État partagé entre tous les agents ────────────────────────────────────────

class AgentState(TypedDict):
    """
    État partagé transmis entre les nœuds du graphe LangGraph.

    Chaque agent lit et enrichit cet état :
    - research_node   → remplit retrieved_docs
    - analysis_node   → remplit analysis
    - writing_node    → remplit draft_response, incrémente iteration_count
    - validation_node → remplit is_valid, feedback, final_response, validation_score
    """
    question: str                    # Question originale de l'étudiant
    retrieved_docs: Optional[str]    # Passages RAG extraits par Agent Recherche
    analysis: Optional[str]          # Synthèse de l'Agent Analyse
    draft_response: Optional[str]    # Brouillon de l'Agent Rédaction
    final_response: Optional[str]    # Réponse finale validée
    is_valid: Optional[bool]         # Verdict de l'Agent Validation
    feedback: Optional[str]          # Feedback pour révision
    iteration_count: int             # Compteur d'itérations (anti-boucle infinie)
    validation_score: Optional[int]  # Score de qualité 0-100


# ── Nœuds du graphe ───────────────────────────────────────────────────────────

def research_node(state: AgentState) -> AgentState:
    """
    Nœud 1 — Agent Recherche.
    Interroge ChromaDB via LlamaIndex (RAG) pour extraire les passages pertinents.
    """
    print("\n" + "═" * 60)
    print("🔍  AGENT RECHERCHE  (RAG via LlamaIndex + ChromaDB)")
    print("═" * 60)
    retrieved = run_research(state["question"])
    return {**state, "retrieved_docs": retrieved}


def analysis_node(state: AgentState) -> AgentState:
    """
    Nœud 2 — Agent Analyse.
    Synthétise les passages et identifie les informations clés.
    """
    print("\n" + "═" * 60)
    print("🧠  AGENT ANALYSE  (synthèse & structuration)")
    print("═" * 60)
    analysis = run_analysis(
        question=state["question"],
        retrieved_docs=state.get("retrieved_docs") or "Aucune information récupérée.",
    )
    return {**state, "analysis": analysis}


def writing_node(state: AgentState) -> AgentState:
    """
    Nœud 3 — Agent Rédaction.
    Rédige la réponse pour l'étudiant. Intègre le feedback si disponible.
    """
    print("\n" + "═" * 60)
    print("✍️   AGENT RÉDACTION  (formulation de la réponse)")
    print("═" * 60)
    draft = run_writing(
        question=state["question"],
        analysis=state.get("analysis") or "",
        feedback=state.get("feedback") or "",
    )
    return {
        **state,
        "draft_response": draft,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def validation_node(state: AgentState) -> AgentState:
    """
    Nœud 4 — Agent Validation.
    Évalue la qualité. Si insuffisante, génère un feedback pour l'Agent Rédaction.
    """
    print("\n" + "═" * 60)
    print("🔎  AGENT VALIDATION  (contrôle qualité)")
    print("═" * 60)
    result = run_validation(
        question=state["question"],
        draft_response=state.get("draft_response") or "",
        retrieved_docs=state.get("retrieved_docs") or "",
    )
    is_valid = result.get("is_valid", True)
    return {
        **state,
        "is_valid": is_valid,
        "feedback": result.get("feedback", ""),
        "final_response": state["draft_response"] if is_valid else None,
        "validation_score": result.get("score", 0),
    }


# ── Routage conditionnel ───────────────────────────────────────────────────────

def should_revise(state: AgentState) -> str:
    """
    Décide si on valide ou si on révise la réponse.

    Logique :
    - Réponse valide                → "end"
    - Max itérations atteint        → "end" (sécurité anti-boucle infinie)
    - Réponse insuffisante          → "revise" (retour à writing_node)
    """
    if state.get("is_valid"):
        print("\n✅  Réponse VALIDÉE — fin du workflow.")
        return "end"
    iteration = state.get("iteration_count", 0)
    if iteration >= MAX_VALIDATION_RETRIES:
        print(f"\n⚠️  Limite de {MAX_VALIDATION_RETRIES} itérations atteinte — finalisation.")
        return "end"
    print(f"\n🔄  Révision demandée (itération {iteration}/{MAX_VALIDATION_RETRIES})...")
    return "revise"


# ── Construction et compilation du graphe ─────────────────────────────────────

def build_graph():
    """
    Construit et compile le StateGraph LangGraph.

    Transitions :
        research ──► analysis ──► writing ──► validation ──┬──► END
                                       ▲____________________|  (si révision)
    """
    graph = StateGraph(AgentState)

    # Enregistrement des nœuds
    graph.add_node("research", research_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("writing", writing_node)
    graph.add_node("validation", validation_node)

    # Flux séquentiel
    graph.set_entry_point("research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "writing")
    graph.add_edge("writing", "validation")

    # Routage conditionnel après validation
    graph.add_conditional_edges(
        "validation",
        should_revise,
        {"end": END, "revise": "writing"},
    )

    return graph.compile()


# ── Point d'entrée public ─────────────────────────────────────────────────────

def run_system(question: str) -> dict:
    """
    Lance le système multi-agents complet sur une question étudiant.

    Args:
        question: La question en langage naturel.

    Returns:
        dict avec les clés :
          - final_response (str)   : réponse prête pour l'étudiant
          - validation_score (int) : score qualité 0-100
          - iteration_count (int)  : nb d'itérations effectuées
          - retrieved_docs (str)   : contexte RAG utilisé (pour démo)
    """
    app = build_graph()

    initial_state: AgentState = {
        "question": question,
        "retrieved_docs": None,
        "analysis": None,
        "draft_response": None,
        "final_response": None,
        "is_valid": None,
        "feedback": None,
        "iteration_count": 0,
        "validation_score": None,
    }

    final_state = app.invoke(initial_state)

    # Sécurité : si final_response non défini, on utilise le brouillon
    if not final_state.get("final_response"):
        final_state["final_response"] = final_state.get(
            "draft_response",
            "Je n'ai pas pu générer une réponse satisfaisante pour cette question."
        )

    return final_state
