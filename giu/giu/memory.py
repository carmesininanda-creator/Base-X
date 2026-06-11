"""
Memória da Vida — o coração da Giu.

Três tipos de memória:
- Perfil:    quem é a pessoa (nome, pessoas importantes, preferências)
- Fatos:     memória semântica ("Nanda prefere resolver tudo por voz")
- Conversas: memória episódica (histórico de mensagens por canal)

Mais a Agenda Viva e os Lembretes, que são memória do futuro.
"""

import json
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config


def _conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                user_id    TEXT PRIMARY KEY,
                name       TEXT,
                data       TEXT DEFAULT '{}',
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS facts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                category   TEXT DEFAULT 'geral',
                content    TEXT NOT NULL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                channel    TEXT DEFAULT 'web',
                role       TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS agenda (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                title      TEXT NOT NULL,
                date       TEXT,
                time       TEXT,
                notes      TEXT,
                done       INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                channel    TEXT DEFAULT 'web',
                text       TEXT NOT NULL,
                due_at     TEXT NOT NULL,
                sent       INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_actions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      TEXT NOT NULL,
                type         TEXT NOT NULL,
                summary      TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                risk_level   TEXT DEFAULT 'baixo',
                status       TEXT DEFAULT 'pending',
                created_at   TEXT,
                confirmed_at TEXT,
                executed_at  TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id);
            CREATE INDEX IF NOT EXISTS idx_facts_user ON facts(user_id, id);
            CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(sent, due_at);
            CREATE INDEX IF NOT EXISTS idx_actions_user ON pending_actions(user_id, status);
        """)


def _now():
    """Agora no fuso configurado, salvo como horário local naive (comparável por string)."""
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None).isoformat(timespec="seconds")


# ─── Perfil ───────────────────────────────────────────────────────────────────

def get_profile(user_id):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM profile WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        return {"user_id": user_id, "name": None, "data": {}}
    return {"user_id": row["user_id"], "name": row["name"], "data": json.loads(row["data"] or "{}")}


def set_profile(user_id, name=None, **data):
    profile = get_profile(user_id)
    name = name or profile["name"]
    merged = {**profile["data"], **data}
    with _conn() as conn:
        conn.execute(
            """INSERT INTO profile (user_id, name, data, created_at) VALUES (?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, data=excluded.data""",
            (user_id, name, json.dumps(merged, ensure_ascii=False), _now()),
        )


# ─── Fatos (memória semântica) ────────────────────────────────────────────────

def remember_fact(user_id, content, category="geral"):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO facts (user_id, category, content, created_at) VALUES (?,?,?,?)",
            (user_id, category, content, _now()),
        )


def get_facts(user_id, limit=40):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, category, content FROM facts WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [{"id": r["id"], "category": r["category"], "content": r["content"]} for r in reversed(rows)]


def delete_fact(user_id, fact_id):
    with _conn() as conn:
        cur = conn.execute("DELETE FROM facts WHERE user_id=? AND id=?", (user_id, fact_id))
        return cur.rowcount > 0


def search_facts(user_id, query, limit=10):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT category, content FROM facts WHERE user_id=? AND content LIKE ? ORDER BY id DESC LIMIT ?",
            (user_id, f"%{query}%", limit),
        ).fetchall()
    return [{"category": r["category"], "content": r["content"]} for r in rows]


# ─── Conversas (memória episódica) ────────────────────────────────────────────

def save_message(user_id, role, content, channel="web"):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, channel, role, content, created_at) VALUES (?,?,?,?,?)",
            (user_id, channel, role, content, _now()),
        )


def get_history(user_id, limit=16):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def message_count(user_id):
    with _conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM messages WHERE user_id=?", (user_id,)).fetchone()[0]


# ─── Agenda Viva ──────────────────────────────────────────────────────────────

def add_agenda(user_id, title, date=None, time=None, notes=None):
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO agenda (user_id, title, date, time, notes, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, title, date, time, notes, _now()),
        )
        return cur.lastrowid


def get_agenda(user_id, include_done=False):
    sql = "SELECT id, title, date, time, notes, done FROM agenda WHERE user_id=?"
    if not include_done:
        sql += " AND done=0"
    sql += " ORDER BY date IS NULL, date, time"
    with _conn() as conn:
        rows = conn.execute(sql, (user_id,)).fetchall()
    return [dict(r) for r in rows]


def complete_agenda(user_id, item_id):
    with _conn() as conn:
        cur = conn.execute("UPDATE agenda SET done=1 WHERE user_id=? AND id=?", (user_id, item_id))
        return cur.rowcount > 0


# ─── Lembretes ────────────────────────────────────────────────────────────────

def add_reminder(user_id, text, due_at, channel="web"):
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO reminders (user_id, channel, text, due_at, created_at) VALUES (?,?,?,?,?)",
            (user_id, channel, text, due_at, _now()),
        )
        return cur.lastrowid


def due_reminders():
    """Lembretes vencidos e ainda não enviados — usados pelo scheduler."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, user_id, channel, text, due_at FROM reminders WHERE sent=0 AND due_at <= ?",
            (_now(),),
        ).fetchall()
    return [dict(r) for r in rows]


def mark_reminder_sent(reminder_id):
    with _conn() as conn:
        conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (reminder_id,))


def reminders_today(user_id):
    """Lembretes ainda não enviados com vencimento hoje."""
    today = _now()[:10]
    with _conn() as conn:
        rows = conn.execute(
            "SELECT text, due_at FROM reminders WHERE user_id=? AND sent=0 AND substr(due_at,1,10)=?",
            (user_id, today),
        ).fetchall()
    return [dict(r) for r in rows]


def push_users():
    """Usuários alcançáveis proativamente: (user_id, canal da última conversa com push)."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT user_id, channel FROM messages WHERE id IN ("
            "  SELECT MAX(id) FROM messages WHERE channel IN ('whatsapp','telegram') GROUP BY user_id"
            ")"
        ).fetchall()
    return [(r["user_id"], r["channel"]) for r in rows]


# ─── Ações Pendentes (execução com autorização real) ──────────────────────────

def add_pending_action(user_id, action_type, summary, payload, risk_level="baixo"):
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO pending_actions (user_id, type, summary, payload_json, risk_level, created_at)
               VALUES (?,?,?,?,?,?)""",
            (user_id, action_type, summary, json.dumps(payload, ensure_ascii=False), risk_level, _now()),
        )
        return cur.lastrowid


def get_pending_action(user_id, action_id):
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM pending_actions WHERE user_id=? AND id=?", (user_id, action_id)
        ).fetchone()
    if not row:
        return None
    action = dict(row)
    action["payload"] = json.loads(action.pop("payload_json"))
    return action


def list_pending_actions(user_id):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, type, summary, risk_level, created_at FROM pending_actions "
            "WHERE user_id=? AND status='pending' ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def mark_action_executed(user_id, action_id):
    now = _now()
    with _conn() as conn:
        conn.execute(
            "UPDATE pending_actions SET status='executed', confirmed_at=?, executed_at=? "
            "WHERE user_id=? AND id=?",
            (now, now, user_id, action_id),
        )
