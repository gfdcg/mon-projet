"""
Génération des documents universitaires de test pour le pipeline RAG.

Ce script crée des données privées réalistes simulant la documentation
d'une université : règlement, guide étudiant, catalogue, calendrier, FAQ.

Usage : python scripts/generate_data.py
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_pdf(filename: str, title: str, sections: list[dict]):
    """Génère un PDF avec titre et sections."""
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
textColor=HexColor("#1a237e"), fontSize=18)
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
                        textColor=HexColor("#283593"), fontSize=13)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                            textColor=HexColor("#3949ab"), fontSize=11)
    body_style = styles["BodyText"]
    body_style.leading = 16

    story = [Paragraph(title, title_style), Spacer(1, 0.5*cm)]
    for sec in sections:
        story.append(Paragraph(sec["heading"], h1_style))
        story.append(Spacer(1, 0.2*cm))
        for item in sec["content"]:
            if item.startswith("##"):
                story.append(Paragraph(item[2:].strip(), h2_style))
            else:
                story.append(Paragraph(item, body_style))
            story.append(Spacer(1, 0.1*cm))
        story.append(Spacer(1, 0.4*cm))

    doc.build(story)
    print(f"[Données] ✅ Créé : {path.name}")


def generate_reglement():
    make_pdf("reglement_interieur.pdf",
            "Règlement Intérieur — Université Ibn Khaldoun",
            [
        {"heading": "Article 1 — Assiduité et Présence",
          "content": [
              "La présence aux cours magistraux, travaux dirigés et travaux pratiques est "
              "OBLIGATOIRE pour tous les étudiants inscrits.",
              "Un étudiant ayant plus de 20% d'absences non justifiées dans une matière est "
              "déclaré défaillant et ne peut se présenter à l'examen de cette matière.",
              "Les absences justifiées (maladie, décès familial) doivent être signalées au "
              "secrétariat dans un délai de 72 heures et accompagnées d'un justificatif officiel.",
              "## Calcul des absences",
              "Chaque séance = 1h30. Le seuil de 20% est calculé sur le total des séances "
              "programmées par matière sur le semestre.",
          ]},
         {"heading": "Article 2 — Examens et Évaluation",
          "content": [
              "L'année universitaire est divisée en deux semestres. Chaque semestre comprend "
              "une session d'examen normale et une session de rattrapage.",
              "La note finale d'une matière = 40% Contrôle Continu (CC) + 60% Examen Final.",
              "Le contrôle continu comprend : interrogations écrites, exposés, projets et devoirs.",
              "## Conditions de passage à l'année supérieure",
              "Pour valider son année, l'étudiant doit obtenir une moyenne générale >= 10/20 "
              "avec au moins 10/20 dans chaque UE (Unité d'Enseignement).",
              "Un étudiant ayant entre 8/20 et 9.99/20 de moyenne générale peut passer en "
              "jury de délibération. Le jury peut décider du passage exceptionnel.",
              "## Session de rattrapage",
              "La session de rattrapage a lieu 3 semaines après les résultats de la session "
              "normale. Seules les matières avec une note < 10/20 peuvent être repassées.",
              "La note de rattrapage remplace la note de la session normale si elle est supérieure.",
          ]},
         {"heading": "Article 3 — Discipline et Sanctions",
          "content": [
              "Tout acte de triche aux examens entraîne automatiquement la note 0 dans la "
              "matière concernée et une convocation devant le conseil de discipline.",
              "L'utilisation des téléphones portables en salle d'examen est strictement interdite.",
              "Le plagiat dans les travaux académiques est considéré comme une faute grave "
              "et peut entraîner l'annulation du travail et des sanctions disciplinaires.",
              "## Conseil de discipline",
              "Le conseil de discipline peut prononcer : avertissement, blâme, suspension "
              "temporaire (1 à 6 mois), ou exclusion définitive de l'établissement.",
          ]},
         {"heading": "Article 4 — Inscriptions et Réinscriptions",
          "content": [
              "L'inscription administrative est obligatoire chaque année universitaire. "
              "Elle ouvre droit à la carte étudiant et aux services universitaires.",
              "La réinscription doit être effectuée avant le 30 septembre de chaque année.",
              "Les droits d'inscription sont fixés annuellement par arrêté ministériel.",
              "Un étudiant non réinscrit dans les délais peut perdre sa place. Des dérogations "
              "exceptionnelles peuvent être accordées sur justification.",
              "## Documents requis pour l'inscription",
              "- Formulaire d'inscription dûment rempli et signé",
              "- Copie du baccalauréat ou du diplôme équivalent",
              "- 4 photos d'identité récentes",
              "- Certificat médical de moins de 3 mois",
              "- Reçu de paiement des droits d'inscription",
          ]},
         {"heading": "Article 5 — Droits et Obligations des Étudiants",
          "content": [
              "Tout étudiant a le droit d'accéder aux bibliothèques, salles informatiques "
              "et espaces de travail de l'université pendant les heures d'ouverture.",
              "Les étudiants ont le droit de consulter leurs copies d'examen dans un délai "
              "de 15 jours après la proclamation des résultats.",
              "Les étudiants sont tenus de respecter les horaires des cours et de se "
              "comporter de manière respectueuse envers les enseignants et le personnel.",
          ]},
     ])


def generate_guide_etudiant():
    make_pdf("guide_etudiant.pdf",
             "Guide de l'Étudiant — Université Ibn Khaldoun",
             [
         {"heading": "Bienvenue à l'Université Ibn Khaldoun",
          "content": [
              "Ce guide vous accompagnera tout au long de votre parcours universitaire. "
              "Il regroupe les informations essentielles sur les services, les procédures "
              "et la vie étudiante au sein de notre établissement.",
          ]},
         {"heading": "Services Administratifs",
          "content": [
              "## Secrétariat Pédagogique",
              "Horaires d'ouverture : Lundi–Jeudi 8h00–16h00, Vendredi 8h00–12h00.",
              "Le secrétariat gère : les inscriptions, les relevés de notes, les attestations "
              "de scolarité, les demandes de transfert et les équivalences.",
              "## Demande d'attestation de scolarité",
              "Déposez votre demande au secrétariat avec une copie de la carte étudiante. "
              "Le délai de traitement est de 3 jours ouvrables.",
              "## Relevé de notes officiel",
              "Le relevé de notes officiel est disponible après chaque session d'examens "
              "sur l'espace numérique étudiant (ENE) ou au secrétariat.",
          ]},
         {"heading": "Espace Numérique Étudiant (ENE)",
          "content": [
              "L'ENE est accessible à l'adresse : ene.univ-ibnkhaldoun.dz",
              "Votre identifiant = votre numéro de matricule étudiant.",
              "Mot de passe initial = les 6 premiers chiffres de votre date de naissance (JJMMAA).",
              "## Fonctionnalités de l'ENE",
              "- Consultation des emplois du temps",
              "- Accès aux notes et résultats d'examens",
              "- Téléchargement des supports de cours",
              "- Dépôt des travaux et projets",
              "- Inscription aux examens de rattrapage",
              "- Communication avec les enseignants",
          ]},
         {"heading": "Procédure de Transfert Inter-Établissements",
          "content": [
              "Un étudiant souhaitant se transférer dans une autre université doit suivre "
              "les étapes suivantes :",
              "Étape 1 : Obtenir une attestation de départ auprès du secrétariat de l'université "
              "d'origine (délai : 5 jours ouvrables).",
              "Étape 2 : Déposer un dossier de transfert à l'université d'accueil avant le "
              "15 octobre (transfert de S1 vers S1) ou le 15 mars (transfert de S2 vers S2).",
              "Étape 3 : Le dossier est examiné par la commission pédagogique. "
              "Réponse dans un délai de 15 jours.",
              "Étape 4 : En cas d'acceptation, procéder à l'inscription administrative "
              "dans l'établissement d'accueil.",
              "## Documents requis pour le transfert",
              "- Relevés de notes de toutes les années étudiées",
              "- Attestation de départ de l'université d'origine",
              "- Lettre de motivation (1 page maximum)",
              "- Programme des matières déjà validées",
          ]},
         {"heading": "Bourses et Aides Sociales",
          "content": [
              "Les étudiants peuvent bénéficier d'une bourse d'études sous conditions "
              "de ressources familiales et de résultats académiques.",
              "Le dossier de bourse est à déposer avant le 31 octobre pour l'année en cours.",
              "## Conditions d'attribution",
              "- Être régulièrement inscrit en formation initiale",
              "- Avoir validé l'année précédente (moyenne >= 10/20)",
              "- Justifier d'un quotient familial inférieur au seuil fixé",
              "Le montant de la bourse est de 3000 DA/mois pour le taux normal "
              "et 4500 DA/mois pour le taux majoré.",
          ]},
     ])


def generate_catalogue_cours():
    make_pdf("catalogue_cours.pdf",
             "Catalogue des Cours — Licence Informatique",
             [
         {"heading": "Semestre 1 — L1",
          "content": [
              "## INF101 — Introduction à la Programmation (6 ECTS)",
              "Prérequis : Aucun. Enseignant : Dr. Kamel Bouzid.",
              "Contenu : Bases algorithmiques, structures de données élémentaires, "
              "programmation en Python. Introduction aux boucles, conditions, fonctions et listes.",
              "Évaluation : CC 40% (2 interrogations) + Examen final 60%.",
              "## MAT101 — Mathématiques Discrètes (5 ECTS)",
              "Prérequis : Aucun. Enseignant : Dr. Samira Hadjali.",
              "Contenu : Logique propositionnelle, ensembles, relations, fonctions, graphes, "
              "arithmétique modulaire, combinatoire.",
              "Évaluation : CC 40% + Examen final 60%.",
              "## ANG101 — Anglais Technique I (3 ECTS)",
              "Enseignant : Mme. Rima Messaoud. Contenu : Vocabulaire technique informatique, "
              "lecture d'articles scientifiques, rédaction de rapports.",
          ]},
         {"heading": "Semestre 2 — L1",
          "content": [
              "## INF102 — Programmation Orientée Objet (6 ECTS)",
              "Prérequis : INF101. Enseignant : Dr. Yacine Khennoufa.",
              "Contenu : Classes, objets, héritage, polymorphisme, encapsulation. "
              "Implémentation en Java. Design patterns de base.",
              "Évaluation : CC 40% (projet + interrogation) + Examen final 60%.",
              "## INF103 — Systèmes d'Exploitation (4 ECTS)",
              "Prérequis : INF101. Enseignant : Dr. Amina Djebbari.",
              "Contenu : Gestion des processus, mémoire, fichiers. Shell Linux, "
              "scripts Bash. Notions de virtualisation.",
              "## MAT102 — Algèbre Linéaire (5 ECTS)",
              "Prérequis : MAT101. Contenu : Espaces vectoriels, matrices, déterminants, "
              "valeurs propres. Applications à l'informatique graphique.",
          ]},
         {"heading": "Semestre 3 — L2",
          "content": [
              "## INF201 — Structures de Données Avancées (6 ECTS)",
              "Prérequis : INF102. Enseignant : Dr. Farouk Talbi.",
              "Contenu : Arbres binaires, arbres AVL, tas, tables de hachage, "
              "graphes et algorithmes de parcours (BFS, DFS).",
              "Évaluation : CC 40% (TP notés + interrogation) + Examen 60%.",
              "## INF202 — Bases de Données (5 ECTS)",
              "Prérequis : INF101. Enseignant : Dr. Nadia Boukhalfa.",
              "Contenu : Modèle entité-association, SQL, normalisation, transactions. "
              "Travaux pratiques sur PostgreSQL.",
              "## INF203 — Réseaux Informatiques (5 ECTS)",
              "Contenu : Modèle OSI, TCP/IP, routage, sécurité réseau de base. "
              "Configuration de réseaux locaux en TP.",
          ]},
         {"heading": "Semestre 5 — L3",
          "content": [
              "## INF301 — Intelligence Artificielle (6 ECTS)",
              "Prérequis : INF201, MAT102. Enseignant : Dr. Sofiane Larabi.",
              "Contenu : Recherche heuristique, apprentissage automatique, réseaux de neurones, "
              "traitement du langage naturel. Projet de fin de semestre obligatoire.",
              "## INF302 — Génie Logiciel (5 ECTS)",
              "Contenu : Méthodes Agile, UML, tests unitaires, intégration continue, "
              "gestion de projet Git.",
              "## INF303 — IA Distribuée et Systèmes Multi-Agents (5 ECTS)",
              "Prérequis : INF301. Enseignant : Dr. Mohamed Benali.",
              "Contenu : Agents BDI, protocoles multi-agents, LangChain, LlamaIndex, "
              "RAG (Retrieval-Augmented Generation), orchestration d'agents LLM.",
              "Évaluation : Projet binôme 60% + Soutenance 40%.",
          ]},
     ])


def generate_calendrier():
    content = """CALENDRIER ACADÉMIQUE — UNIVERSITÉ IBN KHALDOUN
Année Universitaire 2025–2026
================================================

SEMESTRE 1
----------
Début des cours S1        : 15 septembre 2025
Contrôle continu 1 (CC1)  : Semaine du 20 octobre 2025
Contrôle continu 2 (CC2)  : Semaine du 24 novembre 2025
Fin des cours S1          : 12 décembre 2025
Examens S1 (session normale): 15 décembre 2025 – 3 janvier 2026
Résultats S1              : 15 janvier 2026
Session rattrapage S1     : 26 – 31 janvier 2026
Résultats rattrapage S1   : 7 février 2026

SEMESTRE 2
----------
Début des cours S2        : 15 février 2026
Contrôle continu 1 (CC1)  : Semaine du 23 mars 2026
Contrôle continu 2 (CC2)  : Semaine du 27 avril 2026
Fin des cours S2          : 15 mai 2026
Examens S2 (session normale): 18 mai – 5 juin 2026
Résultats S2              : 20 juin 2026
Session rattrapage S2     : 29 juin – 4 juillet 2026
Résultats rattrapage S2   : 12 juillet 2026
Délibérations annuelles   : 15–20 juillet 2026

VACANCES ET JOURS FÉRIÉS
-------------------------
Vacances Toussaint        : 1–7 novembre 2025
Vacances de Noël          : 25 décembre 2025 – 4 janvier 2026
Fête de l'Indépendance    : 1er novembre (Jour férié)
Aid El Fitr               : Selon calendrier lunaire (~mars 2026)
Aid El Adha               : Selon calendrier lunaire (~juin 2026)

ÉVÉNEMENTS ACADÉMIQUES
----------------------
Journée Portes Ouvertes   : 25 octobre 2025
Forum de l'Emploi         : 12 mars 2026
Remise des diplômes L3    : 20 juillet 2026
Dépôt mémoires L3        : avant le 30 avril 2026

DÉLAIS ADMINISTRATIFS IMPORTANTS
----------------------------------
Réinscription             : avant le 30 septembre 2025
Demande de bourse         : avant le 31 octobre 2025
Demande de transfert S1   : avant le 15 octobre 2025
Demande de transfert S2   : avant le 15 mars 2026
Demande d'équivalence     : avant le 1er novembre 2025
Inscription examens rattrap: Dans les 72h suivant la publication des résultats
"""
    path = OUTPUT_DIR / "calendrier_academique.txt"
    path.write_text(content, encoding="utf-8")
    print(f"[Données] ✅ Créé : {path.name}")


def generate_faq():
    faq = {
        "titre": "FAQ Étudiants — Université Ibn Khaldoun",
        "questions": [
            {
                "id": "FAQ001",
                "question": "Comment obtenir une attestation de scolarité ?",
                "reponse": (
                    "Rendez-vous au secrétariat pédagogique (bâtiment A, RDC) "
                    "avec votre carte étudiante. Déposez votre demande écrite. "
                    "L'attestation est prête en 3 jours ouvrables. Vous pouvez aussi "
                    "la télécharger directement depuis l'ENE si vous en avez besoin "
                    "rapidement (version non cachetée)."
                ),
                "categorie": "administratif"
            },
            {
                "id": "FAQ002",
                "question": "Que faire si je rate un examen ?",
                "reponse": (
                    "Si votre note est inférieure à 10/20, vous pouvez vous inscrire "
                    "à la session de rattrapage dans les 72h suivant la publication des "
                    "résultats via l'ENE. La note de rattrapage remplace la note de la "
                    "session normale uniquement si elle est supérieure. Si vous ratez "
                    "également le rattrapage, la matière est à refaire l'année suivante."
                ),
                "categorie": "examens"
            },
            {
                "id": "FAQ003",
                "question": "Combien d'absences sont autorisées par semestre ?",
                "reponse": (
                    "Selon l'article 1 du règlement intérieur, le seuil d'absences "
                    "maximum est fixé à 20% des séances programmées par matière. "
                    "Au-delà, vous êtes déclaré défaillant et exclu de l'examen de la "
                    "matière concernée. Pour un cours de 15 séances, cela représente "
                    "3 absences maximum. Les absences justifiées (avec certificat médical "
                    "déposé dans les 72h) ne sont pas comptabilisées."
                ),
                "categorie": "reglementation"
            },
            {
                "id": "FAQ004",
                "question": "Comment me connecter à l'Espace Numérique Étudiant ?",
                "reponse": (
                    "L'ENE est accessible sur ene.univ-ibnkhaldoun.dz. "
                    "Votre identifiant est votre numéro de matricule étudiant (ex: 20250123). "
                    "Le mot de passe initial est formé des 6 premiers chiffres de votre date "
                    "de naissance au format JJMMAA (ex: pour le 15/03/2002, le mot de passe "
                    "initial est 150302). Changez-le dès votre première connexion."
                ),
                "categorie": "numerique"
            },
            {
                "id": "FAQ005",
                "question": "Quelles sont les conditions pour obtenir une bourse ?",
                "reponse": (
                    "Pour bénéficier d'une bourse universitaire, vous devez : "
                    "(1) Être régulièrement inscrit en formation initiale, "
                    "(2) Avoir validé votre année précédente avec une moyenne >= 10/20, "
                    "(3) Justifier d'un quotient familial inférieur au seuil ministériel. "
                    "Le dossier est à déposer avant le 31 octobre au bureau des affaires sociales. "
                    "Le montant est de 3000 DA/mois (taux normal) ou 4500 DA/mois (taux majoré)."
                ),
                "categorie": "financier"
            },
            {
                "id": "FAQ006",
                "question": "Comment consulter mes notes d'examen ?",
                "reponse": (
                    "Les notes sont publiées sur l'ENE (ene.univ-ibnkhaldoun.dz) "
                    "dans la section 'Mes résultats'. Elles sont disponibles généralement "
                    "2 à 3 semaines après la fin des examens. "
                    "Vous avez le droit de consulter votre copie physique dans les 15 jours "
                    "suivant la publication. Contactez votre enseignant ou le secrétariat "
                    "pour en faire la demande."
                ),
                "categorie": "examens"
            },
            {
                "id": "FAQ007",
                "question": "Quelles sont les conditions de passage en L3 ?",
                "reponse": (
                    "Pour passer de L2 à L3, vous devez : "
                    "(1) Obtenir une moyenne générale >= 10/20 sur l'ensemble de l'année L2, "
                    "(2) Valider toutes les UE (Unités d'Enseignement) avec au moins 10/20. "
                    "Si votre moyenne est entre 8/20 et 9.99/20, votre dossier est examiné "
                    "par le jury de délibération qui peut décider d'un passage exceptionnel. "
                    "En dessous de 8/20, vous devez redoubler l'année."
                ),
                "categorie": "scolarite"
            },
            {
                "id": "FAQ008",
                "question": "Comment déposer un mémoire de fin d'études ?",
                "reponse": (
                    "Le mémoire de L3 doit être déposé avant le 30 avril. "
                    "Vous devez soumettre : "
                    "(1) 3 exemplaires reliés du mémoire (police 12, interligne 1.5), "
                    "(2) Une version numérique sur clé USB (format PDF), "
                    "(3) Le formulaire de dépôt signé par votre encadreur. "
                    "Le dépôt se fait au secrétariat pédagogique. "
                    "La soutenance a lieu en juin-juillet selon le calendrier du département."
                ),
                "categorie": "memoire"
            },
            {
                "id": "FAQ009",
                "question": "Quels cours sont proposés en L3 Informatique ?",
                "reponse": (
                    "En Licence 3 Informatique (S5 et S6), les matières principales sont : "
                    "INF301 Intelligence Artificielle (6 ECTS), "
                    "INF302 Génie Logiciel (5 ECTS), "
                    "INF303 IA Distribuée et Systèmes Multi-Agents (5 ECTS), "
                    "INF304 Sécurité Informatique (4 ECTS), "
                    "INF305 Développement Web Avancé (4 ECTS). "
                    "Le cours INF303 utilise LangChain, LlamaIndex et les LLMs. "
                    "Consultez le catalogue des cours pour les détails complets."
                ),
                "categorie": "pedagogique"
            },
            {
                "id": "FAQ010",
                "question": "Comment contacter un enseignant ?",
                "reponse": (
                    "Vous pouvez contacter vos enseignants via : "
                    "(1) L'ENE : messagerie interne dans 'Mes Cours', "
                    "(2) Les heures de permanence affichées sur la porte de leur bureau, "
                    "(3) Par email institutionnel (prenom.nom@univ-ibnkhaldoun.dz). "
                    "Évitez les contacts via réseaux sociaux personnels. "
                    "Les enseignants ont l'obligation de répondre dans un délai de 5 jours ouvrables."
                ),
                "categorie": "communication"
            }
        ]
    }

    path = OUTPUT_DIR / "faq_etudiants.json"
    path.write_text(json.dumps(faq, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Données] ✅ Créé : {path.name}")


if __name__ == "__main__":
    print("=" * 60)
    print("  Génération des documents universitaires de test")
    print("=" * 60)
    generate_reglement()
    generate_guide_etudiant()
    generate_catalogue_cours()
    generate_calendrier()
    generate_faq()
    print("=" * 60)
    print(f"✅ Tous les documents générés dans : {OUTPUT_DIR}")
    print("   → Lancez ensuite : python scripts/ingest.py")
    print("=" * 60)
