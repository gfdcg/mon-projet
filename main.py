"""
Point d'entrée principal — Assistant Universitaire Multi-Agents.

Interface CLI interactive avec affichage enrichi (Rich).

"""
import sys
import argparse
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.table import Table
from rich import box

console = Console()

DEMO_QUESTIONS = [
    "Quelles sont les conditions de passage en L3 Informatique ?",
    "Combien d'absences sont autorisées par matière au cours du semestre ?",
    "Comment obtenir une attestation de scolarité ?",
    "Quand se déroulent les examens du semestre 2 en 2026 ?",
    "Que se passe-t-il si je rate un examen en session normale ?",
    "Comment me connecter à l'Espace Numérique Étudiant ?",
    "Quels sont les cours disponibles en L3 Informatique ?",
]


def print_banner():
    """Affiche la bannière de démarrage."""
    console.print()
    console.print(Panel.fit(
        Text.assemble(
            ("🎓  Assistant Universitaire Intelligent\n", "bold blue"),
            ("    Système Multi-Agents avec RAG\n", "cyan"),
            ("    LangChain • LlamaIndex • Ollama • ChromaDB", "dim"),
        ),
        border_style="blue",
        padding=(1, 4),
    ))
    console.print()


def print_agent_flow():
    """Affiche le flux des agents."""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Rôle", width=35)
    table.add_column("Technologie", style="dim", width=20)
    table.add_row("🔍 Agent Recherche",  "Interroge la base RAG",         "LlamaIndex + ChromaDB")
    table.add_row("🧠 Agent Analyse",    "Synthétise les passages",        "LangChain LCEL")
    table.add_row("✍️  Agent Rédaction", "Formule la réponse",             "LangChain LCEL")
    table.add_row("🔎 Agent Validation", "Contrôle la qualité",            "LangChain LCEL")
    console.print(table)
    console.print()


def check_index():
    """Vérifie que l'index RAG est disponible."""
    from src.rag.indexing import index_exists
    if not index_exists():
        console.print(Panel(
            "[bold red]❌  Index RAG introuvable !\n\n[/bold red]"
            "[yellow]Lancez d'abord :\n"
            "  1. python scripts/generate_data.py\n"
            "  2. python scripts/ingest.py[/yellow]",
            title="Erreur", border_style="red"
        ))
        sys.exit(1)


def run_query(question: str, show_details: bool = False) -> str:
    """Lance le système multi-agents et affiche les résultats."""
    from src.orchestrator.orchestrator import run_system

    console.print(Rule("[bold cyan]Traitement en cours[/bold cyan]"))
    console.print(f"\n[bold]❓ Question :[/bold] {question}\n")

    # Exécution du système
    result = run_system(question)

    # Affichage de la réponse finale
    console.print()
    console.print(Rule("[bold green]Réponse Finale[/bold green]"))
    console.print(Panel(
        result["final_response"],
        border_style="green",
        padding=(1, 2),
    ))

    # Statistiques
    score = result.get("validation_score") or "N/A"
    iterations = result.get("iteration_count", 1)
    score_color = "green" if isinstance(score, int) and score >= 70 else "yellow"

    stats_table = Table(box=box.SIMPLE, show_header=False)
    stats_table.add_column("Clé", style="dim")
    stats_table.add_column("Valeur", style="bold")
    stats_table.add_row("Score qualité",   f"[{score_color}]{score}/100[/{score_color}]")
    stats_table.add_row("Itérations",      str(iterations))
    stats_table.add_row("Statut",
                        "[green]✅ Validée[/green]" if result.get("is_valid") else "[yellow]⚠️ Acceptée (limite)[/yellow]")
    console.print(stats_table)

    # Affichage du contexte RAG si demandé
    if show_details and result.get("retrieved_docs"):
        console.print(Rule("[dim]Contexte RAG utilisé[/dim]"))
        console.print(Panel(
            result["retrieved_docs"][:1500] + "..." if len(result.get("retrieved_docs", "")) > 1500
            else result.get("retrieved_docs", ""),
            title="[dim]Passages récupérés (LlamaIndex + ChromaDB)[/dim]",
            border_style="dim",
            padding=(0, 1),
        ))

    return result["final_response"]


def run_demo_rag():
    """
    Démonstration comparant RAG vs sans-RAG.
    Montre la valeur ajoutée du pipeline RAG.
    """
    from src.rag.retrieval import retrieve_context
    from langchain_ollama import ChatOllama
    from src.config import OLLAMA_MODEL, OLLAMA_BASE_URL

    console.print(Rule("[bold magenta]🧪  Démonstration RAG vs Sans-RAG[/bold magenta]"))

    question = "Quelles sont les conditions de passage en L3 Informatique ?"
    console.print(f"\n[bold]Question test :[/bold] {question}\n")

    # --- Sans RAG ---
    console.print(Rule("[red]❌  Sans RAG (LLM seul)[/red]"))
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)
    response_without_rag = llm.invoke(question).content
    console.print(Panel(response_without_rag, border_style="red",
                        title="[red]Réponse sans RAG[/red]"))

    # --- Avec RAG ---
    console.print(Rule("[green]✅  Avec RAG (LlamaIndex + ChromaDB)[/green]"))
    context = retrieve_context(question)
    prompt = (
        f"Contexte universitaire :\n{context}\n\n"
        f"Question : {question}\n\n"
        f"Réponds en utilisant uniquement le contexte fourni."
    )
    response_with_rag = llm.invoke(prompt).content
    console.print(Panel(response_with_rag, border_style="green",
                        title="[green]Réponse avec RAG[/green]"))

    console.print("\n[bold green]✅ Le RAG enrichit la réponse avec des données privées précises ![/bold green]")


def interactive_mode():
    """Mode interactif : l'utilisateur pose des questions en continu."""
    console.print("[dim]Tapez [bold]'exit'[/bold] pour quitter, [bold]'demo'[/bold] pour la démonstration[/dim]\n")

    while True:
        try:
            question = console.input("[bold cyan]🎓 Votre question :[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Au revoir ![/dim]")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            console.print("[dim]Au revoir ![/dim]")
            break
        if question.lower() == "demo":
            for i, q in enumerate(DEMO_QUESTIONS[:3], 1):
                console.print(f"\n[dim]--- Question démo {i}/3 ---[/dim]")
                run_query(q)
            continue

        run_query(question)
        console.print()


def main():
    parser = argparse.ArgumentParser(
        description="Assistant Universitaire Multi-Agents (LangChain + LlamaIndex + Ollama)"
    )
    parser.add_argument("--query",    type=str, help="Pose une question directe")
    parser.add_argument("--demo",     action="store_true", help="Lance les questions de démonstration")
    parser.add_argument("--demo-rag", action="store_true", help="Compare RAG vs sans-RAG")
    parser.add_argument("--details",  action="store_true", help="Affiche le contexte RAG utilisé")
    args = parser.parse_args()

    print_banner()
    print_agent_flow()
    check_index()

    if args.demo_rag:
        run_demo_rag()
    elif args.demo:
        console.print(Rule("[bold]Mode Démonstration[/bold]"))
        for i, question in enumerate(DEMO_QUESTIONS, 1):
            console.print(f"\n[bold dim]═══ Question {i}/{len(DEMO_QUESTIONS)} ═══[/bold dim]")
            run_query(question, show_details=args.details)
    elif args.query:
        run_query(args.query, show_details=args.details)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
