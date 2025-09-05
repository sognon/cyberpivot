# main.py — Entrée Streamlit : run bootstrap.sh puis app_cyberpivot.py
import os, subprocess
from pathlib import Path
import importlib
import streamlit as st

st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")

# 1) Lancer bootstrap.sh (optionnel) et afficher les logs
script = Path(__file__).parent / "bootstrap.sh"   # renomme si ton script est bootstrap2.sh
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
        st.error("bootstrap.sh a échoué — convertis tes 'apt' en packages.txt et tes 'pip' en requirements.txt.")
        st.stop()
else:
    st.caption("bootstrap.sh introuvable (ok si tout est déjà préparé).")

# 2) Importer et lancer l'app principale (racine) : app_cyberpivot.py
mod = importlib.import_module("app_cyberpivot")
if hasattr(mod, "main") and callable(mod.main):
    mod.main()

