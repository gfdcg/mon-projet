# 🎓 Assistant Universitaire Multi-Agents

> Système multi-agents intelligent pour accompagner les étudiants universitaires  
> **LangChain · LlamaIndex · Ollama (local) · ChromaDB · LangGraph**

---

## 📋 Cas d'Usage

Ce système aide les étudiants à obtenir des réponses précises sur la vie universitaire :

- 📚 Contenu des cours et syllabus
- 📜 Règlement intérieur et conditions de passage
- 🗓️ Calendrier académique et dates clés
- 🏛️ Procédures administratives (inscriptions, transferts, bourses)
- ❓ Questions fréquentes (FAQ)

Les réponses sont basées sur les **documents privés de l'université** via un pipeline **RAG** — garantissant des informations précises et contextualisées.

---

## 🏗️ Architecture du Système

```
                    ┌──────────────────────────────────┐
  Question          │      ORCHESTRATEUR                │
  Étudiant  ───────►│  LangGraph StateGraph             │
                    └────────────┬─────────────────────┘
                                 │
           ┌─────────────────────▼──────────────────────┐
           │  Flux séquentiel avec feedback conditionnel  │
           │                                              │
           │  [Agent Recherche] ──► [Agent Analyse]       │
           │        │                     │               │
           │        ▼                     ▼               │
           │  RAG (LlamaIndex)    [Agent Rédaction]       │
           │  ChromaDB            ───────────────►        │
           │                      [Agent Validation]      │
           │                           │      │           │
           │                        ✅ END  ❌ Révision  │
           └──────────────────────────────────────────────┘
```

### Les 4 Agents

| Agent | Rôle | Raisonnement | Temperature |
|-------|------|-------------|-------------|
| 🔍 **Agent Recherche** | Interroge ChromaDB via RAG | ReAct | 0.1 |
| 🧠 **Agent Analyse** | Synthétise les passages | Chain-of-thought | 0.2 |
| ✍️ **Agent Rédaction** | Formule la réponse étudiant | Prompt structuré | 0.4 |
| 🔎 **Agent Validation** | Contrôle qualité (score/100) | Critique structurée | 0.1 |

---

## ⚙️ Pipeline RAG (LlamaIndex)

```
Documents Universitaires
(PDF, TXT, JSON)
        │
        ▼ SimpleDirectoryReader
   Chargement
        │
        ▼ SentenceSplitter (512 tokens, overlap 50)
   Chunking
        │
        ▼ nomic-embed-text (Ollama local)
   Embeddings (768 dimensions)
        │
        ▼ ChromaDB (persisté sur disque)
   Stockage Vectoriel
        │
        ▼ Similarité cosinus (Top-K=5)
   Retrieval Sémantique
        │
        ▼
   Contexte → Agent Recherche
```

**Choix techniques justifiés :**
- **SentenceSplitter** : respecte les frontières de phrases (meilleure cohérence sémantique)
- **512 tokens** : équilibre entre contexte riche et précision de l'embedding
- **50 tokens d'overlap** : évite de perdre des informations à cheval entre chunks
- **nomic-embed-text** : modèle d'embedding open-source haute performance, 768 dimensions
- **ChromaDB** : vector store persisté sur disque, sans serveur requis
- **Top-K=5** : 5 passages les plus pertinents — bon compromis précision/contexte

---

## 🛠️ Stack Technologique

| Technologie | Version | Rôle |
|-------------|---------|------|
| Python | 3.10+ | Langage principal |
| LangChain | ≥0.3 | Agents, tools, LCEL |
| LangGraph | ≥0.2 | Orchestration StateGraph |
| LlamaIndex | ≥0.10 | Pipeline RAG complet |
| Ollama | latest | LLM local (mistral) |
| ChromaDB | ≥0.5 | Vector store persisté |
| langchain-ollama | ≥0.2 | Bridge LangChain↔Ollama |

---

## 🗂️ Structure du Projet

```
multiagent/
├── data/
│   ├── raw/                      # Documents universitaires source
│   │   ├── reglement_interieur.pdf
│   │   ├── guide_etudiant.pdf
│   │   ├── catalogue_cours.pdf
│   │   ├── calendrier_academique.txt
│   │   └── faq_etudiants.json
│   └── chroma_db/                # Index vectoriel ChromaDB (auto-généré)
├── src/
│   ├── config.py                 # Configuration centralisée
│   ├── rag/
│   │   ├── ingestion.py          # Chargement + chunking (LlamaIndex)
│   │   ├── indexing.py           # Embeddings + ChromaDB
│   │   └── retrieval.py          # Query engine sémantique
│   ├── tools/
│   │   └── rag_tool.py           # LangChain tools wrappant le RAG
│   ├── agents/
│   │   ├── research_agent.py     # Agent 1 : Recherche (ReAct)
│   │   ├── analysis_agent.py     # Agent 2 : Analyse (LCEL)
│   │   ├── writing_agent.py      # Agent 3 : Rédaction (LCEL)
│   │   └── validation_agent.py   # Agent 4 : Validation (LCEL)
│   └── orchestrator/
│       └── orchestrator.py       # LangGraph StateGraph
├── scripts/
│   ├── generate_data.py          # Génère les documents de test
│   └── ingest.py                 # Lance l'ingestion RAG
├── main.py                       # Point d'entrée CLI
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Installation et Démarrage

### Prérequis

- Python 3.10+
- [Ollama](https://ollama.ai/) installé et démarré

### 1. Cloner et configurer

```bash
cd multiagent
cp .env.example .env
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Télécharger les modèles Ollama

```bash
# LLM principal (génération de texte)
ollama pull mistral

# Modèle d'embedding (vectorisation des documents)
ollama pull nomic-embed-text
```

### 4. Générer les données universitaires de test

```bash
python scripts/generate_data.py
```

### 5. Ingestion RAG (indexation des documents)

```bash
python scripts/ingest.py
```

> ⚠️ Cette étape génère les embeddings et les stocke dans ChromaDB.  
> Elle peut prendre 2-5 minutes selon votre machine.

### 6. Lancer l'assistant

```bash
# Mode interactif (recommandé)
python main.py

# Question directe
python main.py --query "Quelles sont les conditions de passage en L3 ?"

# Démonstration complète
python main.py --demo

# Comparaison RAG vs sans-RAG (pour la soutenance)
python main.py --demo-rag

# Avec affichage du contexte RAG utilisé
python main.py --details
```

---

## 🎯 Démonstration (Soutenance)

### Questions de démonstration recommandées

```bash
# 1. Règlement
python main.py --query "Combien d'absences sont autorisées avant d'être déclaré défaillant ?"

# 2. Procédure administrative
python main.py --query "Comment faire une demande de transfert vers une autre université ?"

# 3. Cours
python main.py --query "Quels sont les prérequis pour le cours INF303 IA Distribuée ?"

# 4. Calendrier
python main.py --query "Quand se déroule la session de rattrapage du semestre 1 ?"

# 5. RAG vs sans-RAG (démonstration de la valeur ajoutée)
python main.py --demo-rag
```

---

## 🔄 Flux d'Orchestration Détaillé

```
Question étudiant
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│ Agent Recherche (ReAct)                                  │
│  Réflexion → Action (rag_tool) → Observation → ...      │
│  Résultat : passages pertinents + sources               │
└─────────────────────────────────────────────────────────┘
      │ retrieved_docs
      ▼
┌─────────────────────────────────────────────────────────┐
│ Agent Analyse (LCEL Chain)                               │
│  Identifie points clés, faits, dates, conditions        │
│  Structure : points clés / faits / manques / synthèse   │
└─────────────────────────────────────────────────────────┘
      │ analysis
      ▼
┌─────────────────────────────────────────────────────────┐
│ Agent Rédaction (LCEL Chain)                             │
│  Rédige réponse claire et structurée pour l'étudiant    │
│  Intègre le feedback si révision demandée               │
└─────────────────────────────────────────────────────────┘
      │ draft_response
      ▼
┌─────────────────────────────────────────────────────────┐
│ Agent Validation (LCEL Chain)                            │
│  Évalue : pertinence + exactitude + complétude + clarté │
│  Score /100 — Seuil de validation : 70/100              │
└─────────────────────────────────────────────────────────┘
      │
      ├── score ≥ 70 ──────────────────────► Réponse finale ✅
      │
      └── score < 70 (max 2 fois) ─────────► Révision 🔄
```

---

## 📊 Données Privées (RAG)

| Document | Format | Contenu |
|----------|--------|---------|
| `reglement_interieur.pdf` | PDF | Assiduité, examens, discipline, inscriptions |
| `guide_etudiant.pdf` | PDF | Services, procédures, ENE, bourses, transferts |
| `catalogue_cours.pdf` | PDF | Cours L1→L3, ECTS, prérequis, enseignants |
| `calendrier_academique.txt` | TXT | Dates S1/S2, examens, vacances, délais |
| `faq_etudiants.json` | JSON | 10 Q&R fréquentes catégorisées |

---

## 🔧 Configuration

Modifiable dans `.env` :

```env
OLLAMA_BASE_URL=http://localhost:11434  # URL Ollama
OLLAMA_MODEL=mistral                    # LLM : mistral / llama3.2 / llama3.1:8b
OLLAMA_EMBED_MODEL=nomic-embed-text     # Embedding model
```

Ou dans `src/config.py` :
```python
CHUNK_SIZE = 512          # Taille des chunks (tokens)
CHUNK_OVERLAP = 50        # Overlap entre chunks
TOP_K = 5                 # Passages récupérés par requête
MAX_VALIDATION_RETRIES = 2  # Max révisions
```

---

## 📝 Évaluation

| Critère | Implémentation |
|---------|---------------|
| **RAG (25%)** | LlamaIndex + ChromaDB + nomic-embed-text, 5 types de documents |
| **Agents (25%)** | 4 agents spécialisés, 3 LangChain tools, prompts ReAct + LCEL |
| **Orchestration (20%)** | LangGraph StateGraph, état partagé, boucle de feedback |
| **Cas d'usage (15%)** | Assistant universitaire, données réalistes, valeur ajoutée |
| **Code & Docs (15%)** | Modulaire, commenté, README complet |

---

*Projet réalisé dans le cadre du module "IA Distribuée et Systèmes Multi-Agents" — Année 2025–2026*
