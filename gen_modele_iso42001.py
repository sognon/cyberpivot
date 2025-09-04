import pandas as pd

# Colonnes attendues par ton code
columns = ["Domain", "QID", "Item", "Question", "Level", "Comment"]

domains = [
    ("Gouvernance & Leadership (AIMS)", "GOV", [
        ("Politique IA", "Existe-t-il une politique IA approuvée couvrant objectifs, portée et responsabilités ?"),
        ("Rôles & responsabilités", "Les rôles (propriétaire de système IA, sponsor, risk owner, DPO, sécurité) sont-ils définis et communiqués ?"),
        ("Comité de gouvernance IA", "Un comité de gouvernance IA se réunit-il régulièrement avec comptes rendus ?"),
        ("Objectifs mesurables", "Des objectifs AIMS (KPI/KRI) sont-ils définis, suivis et revus ?"),
        ("Cartographie des systèmes IA", "L’organisation maintient-elle un inventaire des systèmes IA avec criticité et usage ?"),
    ]),
    ("Gestion des risques IA", "RISK", [
        ("Méthodologie", "La méthodologie d’analyse des risques IA est-elle formalisée et alignée sur l’appétence au risque ?"),
        ("Appréciation des risques", "Les risques IA sont-ils identifiés, évalués et traités avec plans d’actions ?"),
        ("Revues périodiques", "Les risques IA sont-ils revus périodiquement ou lors de changements majeurs ?"),
        ("Acceptation du risque", "Les dérogations et acceptations de risques IA sont-elles tracées et approuvées ?"),
        ("Scénarios d’impact", "Des scénarios d’impact (biais, mésusages, sécurité, sûreté) sont-ils analysés ?"),
    ]),
    ("Données & Dataset", "DATA", [
        ("Origine & licéité", "La provenance, la base légale et les licences des données sont-elles documentées ?"),
        ("Qualité des données", "Des critères de qualité (complétude, exactitude, représentativité) sont-ils définis et suivis ?"),
        ("Gouvernance des labels", "Les processus d’annotation/labeling sont-ils définis, audités et outillés ?"),
        ("Minimisation & rétention", "La minimisation et les durées de conservation des données sont-elles appliquées ?"),
        ("Traçabilité dataset", "La version des jeux de données et leur lignée (data lineage) sont-elles tracées ?"),
    ]),
    ("Conception & Développement", "DEV", [
        ("Spécifications", "Les exigences fonctionnelles, non-fonctionnelles et éthiques du système IA sont-elles spécifiées ?"),
        ("Sécurité by design", "Les exigences de sécurité/robustesse (attaques adversariales, empoisonnement) sont-elles adressées ?"),
        ("Explainability", "Le niveau d’explicabilité requis est-il défini selon l’usage et les parties prenantes ?"),
        ("Contrôles de biais", "Des contrôles de biais/équité sont-ils conçus avec métriques et seuils ?"),
        ("Gestion des dépendances", "Les bibliothèques et modèles tiers (licences, versions, vulnérabilités) sont-ils gérés ?"),
    ]),
    ("Validation & Tests", "VAL", [
        ("Plan de tests", "Un plan de tests IA (fonctionnel, robustesse, sécurité, performance) est-il établi ?"),
        ("Jeux de test", "Des jeux de test indépendants du training set sont-ils utilisés ?"),
        ("Critères d’acceptation", "Des critères d’acceptation avec seuils et tolérances sont-ils approuvés ?"),
        ("Tests de biais/équité", "Des tests de biais/équité sont-ils exécutés et documentés ?"),
        ("Revue indépendante", "Une revue indépendante (4 yeux) est-elle réalisée avant mise en service ?"),
    ]),
    ("Déploiement & Mise en production", "DEP", [
        ("Go/No-Go", "Une procédure Go/No-Go avec risques résiduels validés existe-t-elle ?"),
        ("Sécurisation pipeline", "La CI/CD (MLops) est-elle sécurisée (signatures, scans, secrets) ?"),
        ("Configuration", "Les configurations modèles et hyperparamètres sont-ils versionnés et tracés ?"),
        ("Données en prod", "Les flux et accès aux données de production sont-ils contrôlés et journalisés ?"),
        ("Notice utilisateur", "La documentation utilisateur inclut-elle limites, avertissements et consignes d’usage ?"),
    ]),
    ("Surveillance & Maintenance", "MON", [
        ("Monitoring performance", "Un monitoring en service (drift, qualité, SLA) est-il en place avec alertes ?"),
        ("Recalibrage & retraining", "Des règles de recalibrage/retraining sont-elles définies et tracées ?"),
        ("Logs & traçabilité", "Les décisions/inférences sont-elles journalisées avec contexte suffisant ?"),
        ("Gestion incidents IA", "Existe-t-il un processus d’incident IA (détection, réponse, communication) ?"),
        ("Fin de vie", "Le retrait ou la désactivation contrôlée du système IA est-il prévu ?"),
    ]),
    ("Transparence & Documentation", "DOC", [
        ("Dossier technique", "Un dossier technique (datasheets, model cards) est-il maintenu à jour ?"),
        ("Information parties prenantes", "Les parties prenantes reçoivent-elles une information claire sur l’usage de l’IA ?"),
        ("Traçabilité décisions", "La traçabilité des décisions automatisées est-elle disponible sur demande ?"),
        ("Registre AIMS", "Le registre des systèmes IA et de leur conformité est-il tenu ?"),
        ("Conservation des preuves", "Les preuves de conformité (rapports, validations) sont-elles conservées ?"),
    ]),
    ("Sécurité & Résilience", "SEC", [
        ("Contrôles d’accès", "Les accès aux artefacts IA (modèles, features, données) sont-ils restreints (MFA, RBAC) ?"),
        ("Durcissement & secrets", "Les environnements d’entraînement/inférence sont-ils durcis ; secrets gérés en coffre-fort ?"),
        ("Protection contre attaques IA", "Des mesures contre attaques adversariales/exfiltration sont-elles en place ?"),
        ("Continuité d’activité", "Plans de continuité/reprise couvrent-ils les composants IA critiques ?"),
        ("Tests sécurité", "Des tests sécurité/pentest spécifiques IA sont-ils réalisés ?"),
    ]),
    ("Conformité & Éthique", "COM", [
        ("Conformité RGPD", "Les obligations RGPD (DPIA, droits, transferts, base légale) sont-elles satisfaites ?"),
        ("Éthique & principes", "Des principes éthiques (justice, non-malfaisance, supervision humaine) sont-ils déclinés en contrôles ?"),
        ("Évaluation d’impact", "Des évaluations d’impact (IA Act/DPIA) sont-elles réalisées lorsque requis ?"),
        ("Fournisseurs & tiers", "Les fournisseurs (API/LLM) sont-ils évalués contractuellement (SLA, sécurité, conformité) ?"),
        ("Formation & sensibilisation", "Le personnel impliqué dans l’IA reçoit-il une formation adaptée et régulière ?"),
    ]),
]

rows = []
for domain_name, prefix, items in domains:
    for i, (item, question) in enumerate(items, start=1):
        qid = f"{prefix}-{i:02d}"
        rows.append([domain_name, qid, item, question, "", ""])

df = pd.DataFrame(rows, columns=columns)

# Sauvegarde locale
outfile = "modele_ISO42001_compatible.xlsx"
df.to_excel(outfile, index=False)

print(f"✅ Fichier généré : {outfile}")

