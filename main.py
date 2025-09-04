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
