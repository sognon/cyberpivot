# norms.py
# ============================================================
# Bibliothèque de normes (SQLite)
# - init_norms_db()      : crée la table si absente
# - save_norm(...)       : enregistre/écrase une norme (par tenant + nom)
# - list_norms(tenant)   : liste des normes publiées pour un tenant
# - get_norm_df(...)     : récupère la norme en DataFrame (colonnes harmonisées)
# - delete_norm(...)     : supprime une norme
# ============================================================

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd

DB_PATH = os.getenv("NORMS_DB_PATH", "norms.db")
REQUIRED_COLS = ["Domain", "ID", "Item", "Contrôle", "Level", "Comment"]

def _con():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_norms_db():
    con = _con(); c = con.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS norms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id TEXT NOT NULL,
        name TEXT NOT NULL,
        data_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(tenant_id, name)
    )
    """)
    con.commit(); con.close()

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d = d.rename(columns={"QID": "ID", "Question": "Contrôle"})
    for col in REQUIRED_COLS:
        if col not in d.columns:
            d[col] = ""
        d[col] = d[col].astype("string").fillna("").map(lambda v: str(v) if v is not None else "")
    return d[REQUIRED_COLS].copy()

def save_norm(tenant_id: str, name: str, df: pd.DataFrame) -> Dict:
    name = (name or "").strip()
    if not name:
        raise ValueError("Nom de la norme requis.")
    d = _normalize_columns(df)
    payload = d.to_dict(orient="records")
    now = datetime.utcnow().isoformat()
    con = _con(); c = con.cursor()
    c.execute("""
    INSERT INTO norms(tenant_id, name, data_json, created_at, updated_at)
    VALUES(?,?,?,?,?)
    ON CONFLICT(tenant_id,name) DO UPDATE SET
      data_json=excluded.data_json,
      updated_at=excluded.updated_at
    """, (tenant_id, name, json.dumps(payload, ensure_ascii=False), now, now))
    con.commit()
    c.execute("SELECT id, tenant_id, name, created_at, updated_at FROM norms WHERE tenant_id=? AND name=?",
              (tenant_id, name))
    r = c.fetchone(); con.close()
    return {"id": r[0], "tenant_id": r[1], "name": r[2], "created_at": r[3], "updated_at": r[4]}

def list_norms(tenant_id: str) -> List[Dict]:
    con = _con(); c = con.cursor()
    c.execute("SELECT id, name, created_at, updated_at FROM norms WHERE tenant_id=? ORDER BY name ASC", (tenant_id,))
    rows = c.fetchall(); con.close()
    return [{"id": r[0], "name": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]

def get_norm_df(tenant_id: str, name: str) -> Optional[pd.DataFrame]:
    con = _con(); c = con.cursor()
    c.execute("SELECT data_json FROM norms WHERE tenant_id=? AND name=?", (tenant_id, (name or "").strip()))
    r = c.fetchone(); con.close()
    if not r:
        return None
    try:
        data = json.loads(r[0])
        d = pd.DataFrame(data)
        return _normalize_columns(d)
    except Exception:
        return None

def delete_norm(tenant_id: str, name: str) -> bool:
    con = _con(); c = con.cursor()
    c.execute("DELETE FROM norms WHERE tenant_id=? AND name=?", (tenant_id, (name or "").strip()))
    con.commit()
    ok = c.rowcount > 0
    con.close()
    return ok

