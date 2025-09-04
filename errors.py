# errors.py — affichage & log simple des erreurs

import traceback
import streamlit as st

def report_error(context: str, exc: Exception):
    st.error(f"⚠️ {context} — Une erreur est survenue. Les détails techniques ont été consignés dans les logs.")
    print(f"[ERROR] {context}: {exc}")
    traceback.print_exc()

