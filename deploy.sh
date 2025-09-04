#!/usr/bin/env bash
set -e

# ====== CONFIG ======
# Nom du module principal Streamlit (sans .py). Si ton fichier s'appelle 'streamlit_app.py',
# mets APP_MODULE="streamlit_app"
APP_MODULE="${APP_MODULE:-app}"

# URL SSH du dépôt
REMOTE_SSH="git@github.com:sognon/cyberpivot.git"

echo "➡️  Déploiement CyberPivot (avec bootstrap2.sh) — module: ${APP_MODULE}.py"

# 0) Aller à la racine du repo (même si lancé depuis un sous-dossier)
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# 1) Générer une clé SSH si absente
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
  echo "🔑 Génération d'une clé SSH (ed25519)"
  ssh-keygen -t ed25519 -C "ton_email_github" -N "" -f "$HOME/.ssh/id_ed25519"
  eval "$(ssh-agent -s)"
  ssh-add "$HOME/.ssh/id_ed25519"
  echo "👉 Copie cette clé publique dans GitHub (Settings → SSH and GPG keys → New SSH key):"
  echo "--------------------------------------------------------------------------"
  cat "$HOME/.ssh/id_ed25519.pub"
  echo "--------------------------------------------------------------------------"
  read -p "Appuie sur Entrée après avoir ajouté la clé sur GitHub… " _
else
  eval "$(ssh-agent -s)" >/dev/null
  ssh-add "$HOME/.ssh/id_ed25519" >/dev/null 2>&1 || true
fi

# 2) Bascule le remote en SSH
if git remote | grep -q "^origin$"; then
  git remote set-url origin "$REMOTE_SSH"
else
  git remote add origin "$REMOTE_SSH"
fi

# 3) Créer/mettre à jour main.py — lance bootstrap2.sh puis ton app
cat > main.py <<'PY'
import os, subprocess
from pathlib import Path
import importlib
import streamlit as st

st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")

@st.cache_resource(show_spinner=True)
def run_bootstrap():
    # Exécute bootstrap2.sh s'il existe (sans sudo/apt)
    script = Path(__file__).parent / "bootstrap2.sh"
    if not script.exists():
        return "bootstrap: absent (ok)"
    try:
        os.chmod(script, 0o755)
    except Exception:
        pass
    res = subprocess.run(
        ["/bin/bash", str(script)],
        capture_output=True, text=True
    )
    with st.expander("Logs bootstrap2.sh", expanded=False):
        st.code(res.stdout or "(no stdout)")
        if res.stderr:
            st.code("STDERR:\n" + res.stderr)
    if res.returncode != 0:
        st.error("bootstrap2.sh a échoué — adapte-le (pip -> requirements.txt, apt -> packages.txt).")
        st.stop()
    return "bootstrap: exécuté ✅"

msg = run_bootstrap()
st.write(msg)

# Lancer le module principal (défini via variable d'env APP_MODULE, sinon 'app')
APP_MODULE = os.getenv("APP_MODULE", "app")
try:
    mod = importlib.import_module(APP_MODULE)
    if hasattr(mod, "main") and callable(mod.main):
        mod.main()
except Exception as e:
    st.error(f"Erreur en important {APP_MODULE}.py : {e}")
    st.info("Tu peux changer APP_MODULE dans les Settings Streamlit (env) ou modifier main.py.")
PY

# 4) S'assurer que requirements.txt contient streamlit (et requests si besoin)
grep -q "^streamlit" requirements.txt 2>/dev/null || echo "streamlit" >> requirements.txt
# Si ton bootstrap télécharge des fichiers, requests est utile :
grep -q "^requests" requirements.txt 2>/dev/null || echo "requests" >> requirements.txt

# 5) Commit & push (branche main)
git add -A
git commit -m "Deploy: add main.py entrypoint with bootstrap2.sh runner" || echo "ℹ️ Rien à committer."
git branch -M main
git push --force --set-upstream origin main

echo
echo "✅ Push effectué sur 'main' via SSH."
echo "👉 Sur Streamlit Cloud :"
echo "   - New app (ou Manage app > Deployments) → repo sognon/cyberpivot, branche main"
echo "   - Main file path : main.py"
echo "   - (Optionnel) Variables : APP_MODULE=${APP_MODULE}"
echo "   - Deploy"
echo
echo "🌐 App publique : https://cyberpivot.streamlit.app/"
echo "💡 Si bootstrap2.sh utilise 'apt' ou 'sudo', déclare les paquets dans packages.txt plutôt."

