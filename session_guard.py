# session_guard.py — vérifie l'état de connexion et retourne l'utilisateur

import streamlit as st
import auth

def require_login(auth_status: bool, name: str | None, username: str | None,
                  role_default: str = "user", tenant_default: str = "default"):
    if not auth_status or not username:
        st.sidebar.warning("Veuillez vous connecter pour continuer.")
        st.stop()
    user = auth.get_or_create_user(email=username, full_name=name or username,
                                   role=role_default, tenant_id=tenant_default)
    return user

