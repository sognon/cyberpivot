# errors.py — gestion d'erreurs UI + logs propres
import logging
import streamlit as st

log = logging.getLogger("cyberpivot")

def report_error(context: str, exc: Exception):
    log.exception("[%s] %s", context, exc)
    st.error(f"⚠️ {context} — Une erreur est survenue. Merci de vérifier vos données et réessayer.")
    st.caption("Les détails techniques ont été consignés dans les logs.")

def guard(fn):
    def _wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            report_error(fn.__name__, e)
    return _wrap
