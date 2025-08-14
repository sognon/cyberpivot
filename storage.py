# storage.py — persistance avancée (projets, audits + yaml_path/catalog_hash, réponses)
import os, sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

DB_PATH = os.environ.get("CYBERPIVOT_DB", "cyberpivot.db")

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
    with get_conn() as c:
        c.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                client TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                standard TEXT NOT NULL,
                version TEXT,
                status TEXT DEFAULT 'draft',
                yaml_path TEXT,
                catalog_hash TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                domain TEXT,
                qid TEXT,
                item TEXT,
                question TEXT,
                level TEXT,
                score INTEGER,
                criterion TEXT,
                recommendation TEXT,
                comment TEXT,
                evidence_json TEXT,
                updated_at TEXT NOT NULL,
                UNIQUE(audit_id, qid),
                FOREIGN KEY(audit_id) REFERENCES audits(id)
            );
        """)

def migrate_add_yaml_columns():
    # idempotent
    with get_conn() as c:
        try: c.execute("ALTER TABLE audits ADD COLUMN yaml_path TEXT")
        except Exception: pass
        try: c.execute("ALTER TABLE audits ADD COLUMN catalog_hash TEXT")
        except Exception: pass
        try: c.execute("ALTER TABLE audits ADD COLUMN version TEXT")
        except Exception: pass
        try: c.execute("ALTER TABLE audits ADD COLUMN status TEXT DEFAULT 'draft'")
        except Exception: pass
        try: c.execute("ALTER TABLE audits ADD COLUMN updated_at TEXT")
        except Exception: pass

def create_project(name: str, client: str = "") -> int:
    with get_conn() as c:
        now = datetime.utcnow().isoformat()
        cur = c.execute("INSERT INTO projects(name, client, created_at) VALUES (?, ?, ?)", (name, client, now))
        return cur.lastrowid

def list_projects() -> list[dict]:
    with get_conn() as c:
        rows = c.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def create_audit(project_id: int, standard: str, version: str = "", yaml_path: str = "", catalog_hash: str = "") -> int:
    with get_conn() as c:
        now = datetime.utcnow().isoformat()
        cur = c.execute("""
            INSERT INTO audits(project_id, standard, version, yaml_path, catalog_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, standard, version, yaml_path, catalog_hash, now, now))
        return cur.lastrowid

def update_audit_catalog(audit_id: int, yaml_path: str, catalog_hash: str):
    with get_conn() as c:
        now = datetime.utcnow().isoformat()
        c.execute("UPDATE audits SET yaml_path=?, catalog_hash=?, updated_at=? WHERE id=?",
                  (yaml_path, catalog_hash, now, audit_id))

def list_audits(project_id: Optional[int] = None) -> list[dict]:
    with get_conn() as c:
        if project_id:
            rows = c.execute("SELECT * FROM audits WHERE project_id=? ORDER BY id DESC", (project_id,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM audits ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def upsert_response(audit_id: int, rec: dict) -> None:
    import json
    with get_conn() as c:
        now = datetime.utcnow().isoformat()
        evidence_json = json.dumps(rec.get("evidence", []), ensure_ascii=False)
        c.execute("""
            INSERT INTO responses(audit_id, domain, qid, item, question, level, score, criterion, recommendation, comment, evidence_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(audit_id, qid) DO UPDATE SET
                domain=excluded.domain,
                item=excluded.item,
                question=excluded.question,
                level=excluded.level,
                score=excluded.score,
                criterion=excluded.criterion,
                recommendation=excluded.recommendation,
                comment=excluded.comment,
                evidence_json=excluded.evidence_json,
                updated_at=excluded.updated_at
        """, (
            audit_id, rec.get("domain"), rec.get("qid"), rec.get("item"), rec.get("question"),
            rec.get("level"), rec.get("score"), rec.get("criterion"), rec.get("recommendation"),
            rec.get("comment"), evidence_json, now
        ))

def get_responses(audit_id: int) -> list[dict]:
    with get_conn() as c:
        rows = c.execute("SELECT * FROM responses WHERE audit_id=? ORDER BY qid", (audit_id,)).fetchall()
        return [dict(r) for r in rows]

def delete_audit(audit_id: int) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM responses WHERE audit_id=?", (audit_id,))
        c.execute("DELETE FROM audits WHERE id=?", (audit_id,))

