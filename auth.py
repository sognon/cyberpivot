# auth.py — auth minimaliste SQLite (email, nom, rôle, mot de passe hashé)
import os
import sqlite3
import hashlib
from contextlib import contextmanager
from datetime import datetime

# Chemin de la base (change-le si besoin avec une variable d'env)
DB_PATH = os.environ.get("CYBERPIVOT_DB", "cyberpivot.db")
# Sel basique pour le hash (en prod: change-le et stocke-le côté serveur)
SALT = os.environ.get("CYBERPIVOT_SALT", "cyberpivot_salt_v1")

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """Crée la table users si elle n'existe pas."""
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            pwd_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """)

def _hash_pwd(pwd: str) -> str:
    """Hash SHA-256 avec sel simple (à durcir en prod)."""
    return hashlib.sha256((SALT + pwd).encode("utf-8")).hexdigest()

def create_user(email: str, name: str, role: str, pwd: str):
    """Crée un utilisateur. Rôles permis: admin | auditeur | lecteur."""
    email = (email or "").strip().lower()
    name = (name or "").strip()
    role = role if role in ("admin", "auditeur", "lecteur") else "auditeur"
    if not email or not name or not pwd:
        return False, "Champs requis manquants."
    with get_conn() as c:
        try:
            c.execute(
                "INSERT INTO users(email, name, role, pwd_hash, active, created_at) VALUES (?,?,?,?,?,?)",
                (email, name, role, _hash_pwd(pwd), 1, datetime.utcnow().isoformat()),
            )
            return True, "Utilisateur créé."
        except sqlite3.IntegrityError:
            return False, "Email déjà utilisé."

def authenticate(email: str, pwd: str):
    """Retourne (user_dict, None) si ok, sinon (None, erreur)."""
    email = (email or "").strip().lower()
    with get_conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            return None, "Utilisateur inconnu."
        if row["active"] != 1:
            return None, "Compte désactivé."
        if row["pwd_hash"] != _hash_pwd(pwd or ""):
            return None, "Mot de passe invalide."
        return {
            "id": row["id"],
            "email": row["email"],
            "name": row["name"],
            "role": row["role"],
        }, None

def list_users():
    with get_conn() as c:
        rows = c.execute(
            "SELECT id, email, name, role, active, created_at FROM users ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]

def set_active(user_id: int, active: bool):
    with get_conn() as c:
        c.execute("UPDATE users SET active=? WHERE id=?", (1 if active else 0, user_id))

def reset_password(user_id: int, new_pwd: str):
    with get_conn() as c:
        c.execute("UPDATE users SET pwd_hash=? WHERE id=?", (_hash_pwd(new_pwd), user_id))

