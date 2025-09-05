# main.py — Entrée Streamlit : lance bootstrap.sh puis l'app app_cyberpivot.py
import os, subprocess
from pathlib import Path
import importlib
import streamlit as st

st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")

# 1) Bootstrap (optionnel) — exécuter le script shell et afficher les logs
script = Path(__file__).parent / "bootstrap.sh"
if script.exists():
    try:
        os.chmod(script, 0o755)
    except Exception:
        pass
    res = subprocess.run(["/bin/bash", str(script)], capture_output=True, text=True)
    with st.expander("Logs bootstrap.sh", expanded=False):
        st.code(res.stdout or "(no stdout)")
        if res.stderr:
            st.code("STDERR:\n" + res.stderr)
    if res.returncode != 0:
        st.error("bootstrap.sh a échoué — mets les 'pip' dans requirements.txt, les 'apt' dans packages.txt, et les secrets dans Settings → Secrets.")
        st.stop()
else:
    st.caption("bootstrap.sh introuvable (ok si tout est déjà prêt).")

# 2) Importer et lancer l'app principale
mod = importlib.import_module("app_cyberpivot")
if hasattr(mod, "main") and callable(mod.main):
    mod.main()
