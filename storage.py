# storage.py — persistance SQLite robuste (migration auto + rebuild si schéma critique manquant)

import os
import json
import sqlite3
import datetime
from typing import Any, Dict, Iterable, Set

DB_PATH = os.getenv("DB_PATH", "cyberpivot.db")

def get_conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con

DEST_COLS = [
    "id", "audit_id", "domain", "qid", "item", "question",
    "level", "score", "criterion", "recommendation", "comment",
    "evidence_json", "updated_at"
]

BASE_REQUIRED = {"audit_id", "domain", "qid", "item"}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id   TEXT NOT NULL,
    domain     TEXT NOT NULL,
    qid        TEXT NOT NULL,
    item       TEXT NOT NULL,
    question   TEXT,
    level      TEXT,
    score      REAL,
    criterion  TEXT,
    recommendation TEXT,
    comment    TEXT,
    evidence_json TEXT,
    updated_at TEXT NOT NULL
)
"""

UNIQUE_INDEX_SQL = "CREATE UNIQUE INDEX IF NOT EXISTS uniq_responses_aqi ON responses(audit_id, qid, item)"

def _table_columns(con: sqlite3.Connection, table: str) -> Set[str]:
    cur = con.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return {r[1] for r in cur.fetchall()}

def _table_exists(con: sqlite3.Connection, table: str) -> bool:
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

def _create_fresh(con: sqlite3.Connection):
    c = con.cursor()
    c.execute(CREATE_TABLE_SQL)
    c.execute(UNIQUE_INDEX_SQL)
    con.commit()

def _rebuild_table(con: sqlite3.Connection, existing_cols: Set[str]):
    c = con.cursor()
    c.execute("BEGIN IMMEDIATE")
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses_new(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id   TEXT NOT NULL,
            domain     TEXT NOT NULL,
            qid        TEXT NOT NULL,
            item       TEXT NOT NULL,
            question   TEXT,
            level      TEXT,
            score      REAL,
            criterion  TEXT,
            recommendation TEXT,
            comment    TEXT,
            evidence_json TEXT,
            updated_at TEXT NOT NULL
        )
    """)
    if _table_exists(con, "responses"):
        sel_exprs = []
        sel_exprs.append("COALESCE(audit_id, 'default') AS audit_id" if "audit_id" in existing_cols else "'default' AS audit_id")
        sel_exprs.append("COALESCE(domain, '') AS domain" if "domain" in existing_cols else "'' AS domain")
        sel_exprs.append("COALESCE(qid, '') AS qid" if "qid" in existing_cols else "'' AS qid")
        if "item" in existing_cols:
            sel_exprs.append("COALESCE(item, '') AS item")
        elif "qid" in existing_cols:
            sel_exprs.append("COALESCE(qid, '') AS item")
        else:
            sel_exprs.append("'' AS item")
        sel_exprs.append("question" if "question" in existing_cols else "NULL AS question")
        sel_exprs.append("level" if "level" in existing_cols else "NULL AS level")
        sel_exprs.append("score" if "score" in existing_cols else "NULL AS score")
        sel_exprs.append("criterion" if "criterion" in existing_cols else "NULL AS criterion")
        sel_exprs.append("recommendation" if "recommendation" in existing_cols else "NULL AS recommendation")
        sel_exprs.append("comment" if "comment" in existing_cols else "NULL AS comment")
        sel_exprs.append("evidence_json" if "evidence_json" in existing_cols else "NULL AS evidence_json")
        sel_exprs.append("COALESCE(updated_at, datetime('now')) AS updated_at" if "updated_at" in existing_cols else "datetime('now') AS updated_at")
        select_sql = "SELECT " + ", ".join(sel_exprs) + " FROM responses"
        insert_sql = """
            INSERT INTO responses_new(
                audit_id, domain, qid, item, question, level, score, criterion, recommendation, comment, evidence_json, updated_at
            )
            """ + select_sql
        c.execute(insert_sql)
        c.execute("DROP TABLE responses")

    c.execute("ALTER TABLE responses_new RENAME TO responses")
    c.execute(UNIQUE_INDEX_SQL)
    con.commit()

def _migrate_table(con: sqlite3.Connection):
    if not _table_exists(con, "responses"):
        _create_fresh(con); return
    existing = _table_columns(con, "responses")
    if not BASE_REQUIRED.issubset(existing):
        _rebuild_table(con, existing); return
    c = con.cursor()
    add_stmts = []
    if "question" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN question TEXT")
    if "level" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN level TEXT")
    if "score" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN score REAL")
    if "criterion" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN criterion TEXT")
    if "recommendation" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN recommendation TEXT")
    if "comment" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN comment TEXT")
    if "evidence_json" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN evidence_json TEXT")
    if "updated_at" not in existing: add_stmts.append("ALTER TABLE responses ADD COLUMN updated_at TEXT")
    for stmt in add_stmts: c.execute(stmt)
    c.execute(UNIQUE_INDEX_SQL)
    con.commit()

def init_db():
    con = get_conn()
    _migrate_table(con)
    con.close()

def _as_text(x: Any) -> str:
    if x is None: return ""
    return str(x).strip()

def _evidence_to_json(evidence: Any) -> str:
    if isinstance(evidence, (list, dict)): return json.dumps(evidence, ensure_ascii=False)
    if isinstance(evidence, str): return evidence
    return json.dumps([], ensure_ascii=False)

def upsert_response(audit_id: str, rec: Dict[str, Any]) -> None:
    if not audit_id: raise ValueError("audit_id requis")
    domain = _as_text(rec.get("domain"))
    qid    = _as_text(rec.get("qid"))
    item   = _as_text(rec.get("item"))
    if not domain or not qid or not item:
        raise ValueError(f"Champs requis manquants: domain='{domain}', qid='{qid}', item='{item}'")
    question = _as_text(rec.get("question"))
    level = _as_text(rec.get("level"))
    score = rec.get("score", None)
    criterion = _as_text(rec.get("criterion"))
    recommendation = _as_text(rec.get("recommendation"))
    comment = _as_text(rec.get("comment"))
    evidence_json = _evidence_to_json(rec.get("evidence") or rec.get("evidence_json"))
    now = datetime.datetime.utcnow().isoformat(timespec="seconds")
    con = get_conn(); c = con.cursor()
    c.execute("""
        INSERT INTO responses(audit_id, domain, qid, item, question, level, score, criterion, recommendation, comment, evidence_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(audit_id, qid, item) DO UPDATE SET
            question       = excluded.question,
            level          = excluded.level,
            score          = excluded.score,
            criterion      = excluded.criterion,
            recommendation = excluded.recommendation,
            comment        = excluded.comment,
            evidence_json  = excluded.evidence_json,
            updated_at     = excluded.updated_at
    """, (audit_id, domain, qid, item, question, level, score, criterion, recommendation, comment, evidence_json, now))
    con.commit(); con.close()

def list_responses(audit_id: str) -> Iterable[Dict[str, Any]]:
    con = get_conn(); c = con.cursor()
    c.execute("SELECT * FROM responses WHERE audit_id=? ORDER BY domain, qid, item", (audit_id,))
    rows = [dict(r) for r in c.fetchall()]
    con.close(); return rows

def get_response(audit_id: str, qid: str, item: str):
    con = get_conn(); c = con.cursor()
    c.execute("SELECT * FROM responses WHERE audit_id=? AND qid=? AND item=? LIMIT 1", (audit_id, qid, item))
    row = c.fetchone(); con.close()
    return dict(row) if row else None



