#!/usr/bin/env bash
set -euo pipefail

# --- CONFIG ---------------------------------------------------
APP_FILE="app_cyberpivot_v11_projects_sidebar.py"
DEFAULT_VENV="/home/oscp/Cyberpyvot/venv-cyberpivot"   # ton venv existant
LOCAL_VENV=".venv"                                      # venv fallback si le précédent n'existe pas
DB_PATH="${CYBERPIVOT_DB:-$(pwd)/cyberpivot.db}"        # change via variable d'env si besoin
# --------------------------------------------------------------

echo "▶️  Dossier projet : $(pwd)"
echo "▶️  Base SQLite    : $DB_PATH"

# 1) Python dispo ?
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 introuvable. Installe Python 3."
  exit 1
fi

# 2) Active venv existant OU crée un venv local
if [ -d "$DEFAULT_VENV" ]; then
  echo "✅ Activation du venv existant: $DEFAULT_VENV"
  # shellcheck disable=SC1090
  source "$DEFAULT_VENV/bin/activate"
elif [ -d "$LOCAL_VENV" ]; then
  echo "✅ Activation du venv local: $LOCAL_VENV"
  # shellcheck disable=SC1090
  source "$LOCAL_VENV/bin/activate"
else
  echo "ℹ️  Aucun venv trouvé. Création de $LOCAL_VENV…"
  python3 -m venv "$LOCAL_VENV"
  # shellcheck disable=SC1090
  source "$LOCAL_VENV/bin/activate"
fi

# 3) Upgrade pip + install deps
echo "📦 Installation des dépendances…"
python -m pip install --upgrade pip
pip install streamlit pandas openpyxl python-docx matplotlib pyyaml

# 4) Préparer les dossiers
mkdir -p standards standards/cache templates

# 5) Créer YAML par défaut si absents (n’écrase pas si déjà présents)
if [ ! -f standards/iso42001.yaml ]; then
  cat > standards/iso42001.yaml <<'YAML'
title: ISO/IEC 42001
version: "2024"
domains:
  - name: Gouvernance IA
    controls:
      - id: GOV-1
        item: Politique IA
        question: Existe-t-il une politique IA approuvée et diffusée ?
        objective: Définir le cadre et les responsabilités.
        evidence: Politique signée, date, périmètre.
        reference: ISO 42001 §5
        criterion: Politique approuvée, rôles assignés.
        recommendation: Rédiger/mettre à jour la politique IA.
      - id: GOV-2
        item: Comité IA
        question: Un comité IA supervisant les risques est-il en place ?
        objective: Gouvernance et supervision des risques IA.
        evidence: PV de réunion, charte du comité.
        reference: ISO 42001 §5
        criterion: Réunions régulières, quorum.
        recommendation: Instituer un comité IA avec feuille de route.
  - name: Gestion des risques IA
    controls:
      - id: RSK-1
        item: Méthode risques IA
        question: La méthode de gestion des risques IA est-elle définie et appliquée ?
        objective: Identifier et traiter les risques IA.
        evidence: Méthode documentée, registre des risques.
        reference: ISO 42001 §6
        criterion: Méthode approuvée, revue annuelle.
        recommendation: Formaliser la méthode et maintenir le registre.
YAML
fi

if [ ! -f standards/iso27001.yaml ]; then
  cat > standards/iso27001.yaml <<'YAML'
title: ISO/IEC 27001
version: "2022"
domains:
  - name: Organisation de la sécurité
    controls:
      - id: A.5.1
        item: Politique de sécurité
        question: Les politiques de sécurité sont-elles définies et communiquées ?
        objective: Cadre et orientations sécurité.
        evidence: Politique approuvée, communication.
        reference: ISO 27001 §5
        criterion: Existence, validité, diffusion.
        recommendation: Mettre à jour la politique et communiquer.
  - name: Gestion des actifs
    controls:
      - id: A.5.9
        item: Inventaire des actifs
        question: Un inventaire des actifs est-il maintenu à jour ?
        objective: Connaissance et maîtrise du périmètre.
        evidence: Inventaire, responsables, classification.
        reference: ISO 27001 Annexe A
        criterion: Complet, à jour, assignations.
        recommendation: Mettre en place un inventaire centralisé.
YAML
fi

# 6) Initialiser la base (tables + colonnes yaml_path/catalog_hash si nécessaire)
echo "🗄️  Initialisation DB…"
python - <<'PY'
import os
os.environ.setdefault("CYBERPIVOT_DB", "${DB_PATH}")
import storage
storage.init_db()
try:
    storage.migrate_add_yaml_columns()
except Exception:
    pass
print("DB ok ▶", os.environ["CYBERPIVOT_DB"])
PY

# 7) Lancer Streamlit
echo "🚀 Lancement de l’app Streamlit…"
export CYBERPIVOT_DB="$DB_PATH"
exec streamlit run "$APP_FILE" --server.port 8502

