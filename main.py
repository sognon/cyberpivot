import os, importlib, streamlit as st
st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")
try:
    from cloud_bootstrap import run_bootstrap
    st.caption(run_bootstrap())
except Exception as e:
    st.warning(f"Bootstrap non exécuté: {e}")
mod = importlib.import_module("main.app_cyberpivot")
if hasattr(mod, "main") and callable(mod.main):
    mod.main()