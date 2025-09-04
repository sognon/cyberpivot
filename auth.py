# auth.py
# ============================================================
# Authentification & Gestion des comptes (SQLite)
# - init_auth_db() : crée/migre la table users
# - create_user(), verify_password(), set_password(), set_role(), set_active()
# - update_user_profile(), list_users(), get_user(), get_role()
# - get_or_create_user() : auto-provision (SSO/dev)
# ============================================================

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

from passlib.hash import bcrypt

DB_PATH = os.getenv("AUTH_DB_PATH", "auth.db")

def _con():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_auth_db():
    con = _con()
    c = con.cursor()
    # table principale
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT DEFAULT '',
        role TEXT DEFAULT 'user',
        tenant_id TEXT DEFAULT 'default',
        is_active INTEGER DEFAULT 1,
        pwd_hash TEXT,
        created_at TEXT
    )
    """)
    # migrations non destructives
    cols = {r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()}
    if "tenant_id" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN tenant_id TEXT DEFAULT 'default'")
    if "full_name" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
    if "role" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    if "is_active" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    if "pwd_hash" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN pwd_hash TEXT")
    if "created_at" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    con.commit()

    # bootstrap admin si vide
    c.execute("SELECT COUNT(*) FROM users")
    n = c.fetchone()[0]
    if n == 0:
        now = datetime.utcnow().isoformat()
        pwd_hash = bcrypt.hash("admin")
        c.execute("""
            INSERT INTO users(email, full_name, role, tenant_id, is_active, pwd_hash, created_at)
            VALUES(?,?,?,?,?,?,?)
        """, ("admin@local", "Admin", "admin", "default", 1, pwd_hash, now))
        con.commit()
    con.close()

def _row_to_user(r) -> Dict[str, Any]:
    return {
        "id": r[0], "email": r[1], "full_name": r[2], "role": r[3],
        "tenant_id": r[4], "is_active": bool(r[5]), "pwd_hash": r[6],
        "created_at": r[7],
    }

def create_user(email: str, password: Optional[str], full_name: str = "",
                role: str = "user", tenant_id: str = "default", is_active: bool = True) -> Dict[str, Any]:
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("Email requis")
    con = _con(); c = con.cursor()
    now = datetime.utcnow().isoformat()
    pwd_hash = bcrypt.hash(password) if password else None
    c.execute("""
        INSERT INTO users(email, full_name, role, tenant_id, is_active, pwd_hash, created_at)
        VALUES(?,?,?,?,?,?,?)
    """, (email, full_name or email, role or "user", tenant_id or "default",
          1 if is_active else 0, pwd_hash, now))
    con.commit()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = _row_to_user(c.fetchone()); con.close()
    return user

def user_exists(email: str) -> bool:
    con = _con(); c = con.cursor()
    c.execute("SELECT 1 FROM users WHERE email=?", (email.strip().lower(),))
    r = c.fetchone(); con.close()
    return r is not None

def get_user(email: str) -> Optional[Dict[str, Any]]:
    """➡️ La fonction manquante qui cause ton erreur."""
    con = _con(); c = con.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),))
    r = c.fetchone(); con.close()
    return _row_to_user(r) if r else None

def list_users() -> List[Dict[str, Any]]:
    con = _con(); c = con.cursor()
    c.execute("SELECT * FROM users ORDER BY created_at DESC")
    rows = c.fetchall(); con.close()
    return [_row_to_user(r) for r in rows]

def set_password(email: str, new_password: str):
    if not new_password:
        raise ValueError("Mot de passe requis")
    con = _con(); c = con.cursor()
    c.execute("UPDATE users SET pwd_hash=? WHERE email=?", (bcrypt.hash(new_password), email.strip().lower()))
    con.commit(); con.close()

def set_role(email: str, new_role: str):
    con = _con(); c = con.cursor()
    c.execute("UPDATE users SET role=? WHERE email=?", (new_role, email.strip().lower()))
    con.commit(); con.close()

def set_active(email: str, active: bool):
    con = _con(); c = con.cursor()
    c.execute("UPDATE users SET is_active=? WHERE email=?", (1 if active else 0, email.strip().lower()))
    con.commit(); con.close()

def update_user_profile(email: str, full_name: Optional[str] = None, tenant_id: Optional[str] = None):
    con = _con(); c = con.cursor()
    if full_name is not None:
        c.execute("UPDATE users SET full_name=? WHERE email=?", (full_name, email.strip().lower()))
    if tenant_id is not None:
        c.execute("UPDATE users SET tenant_id=? WHERE email=?", (tenant_id, email.strip().lower()))
    con.commit(); con.close()

def verify_password(email: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(email)
    if not user or not user["is_active"]:
        return None
    if user["pwd_hash"] is None:
        return None
    try:
        ok = bcrypt.verify(password, user["pwd_hash"])
    except Exception:
        ok = False
    return user if ok else None

def get_role(email: str) -> Optional[str]:
    u = get_user(email)
    return u["role"] if u else None

def get_or_create_user(email: str, full_name: Optional[str] = None,
                       role: str = "user", tenant_id: str = "default") -> Dict[str, Any]:
    email = (email or "").strip().lower()
    u = get_user(email)
    if u:
        return u
    return create_user(email=email, password=None, full_name=full_name or email,
                       role=role, tenant_id=tenant_id, is_active=True)




