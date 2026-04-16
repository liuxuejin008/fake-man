"""Postgres persistence for generated images (Neon / standard PostgreSQL)."""
import logging
import os
import threading

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

_schema_lock = threading.Lock()
_schema_ready = False


def database_url():
    return os.environ.get("DATABASE_URL", "").strip() or None


def _connect():
    url = database_url()
    if not url:
        return None
    return psycopg2.connect(url)


def ensure_schema(conn):
    global _schema_ready
    with _schema_lock:
        if _schema_ready:
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS generations (
                    id BIGSERIAL PRIMARY KEY,
                    task_id TEXT UNIQUE,
                    image_url TEXT NOT NULL,
                    prompt TEXT,
                    style TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_generations_created_at
                    ON generations (created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_generations_style_created
                    ON generations (style, created_at DESC);
                """
            )
        conn.commit()
        _schema_ready = True


def save_generation(image_url, prompt=None, style=None, task_id=None):
    """Persist one successful generation. Idempotent per task_id when provided."""
    if not image_url:
        return False
    conn = _connect()
    if not conn:
        return False
    try:
        ensure_schema(conn)
        tid = (str(task_id).strip() if task_id else None) or None
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO generations (task_id, image_url, prompt, style)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (task_id) DO NOTHING
                """,
                (tid, image_url, prompt or "", style or ""),
            )
        conn.commit()
        return True
    except Exception:
        logger.exception("save_generation failed")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        conn.close()


def list_gallery(limit=24, style=None, offset=0):
    """Recent generations, newest first. Optional style (e.g. alternate) and offset."""
    conn = _connect()
    if not conn:
        return []
    try:
        ensure_schema(conn)
        cap = max(1, min(int(limit), 100))
        off = max(0, min(int(offset), 10_000))
        sql_select = """
                SELECT id, image_url, prompt, style, created_at
                FROM generations
                """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if style:
                cur.execute(
                    sql_select
                    + """
                WHERE style = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                    (style, cap, off),
                )
            else:
                cur.execute(
                    sql_select
                    + """
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                    (cap, off),
                )
            rows = cur.fetchall()
        out = []
        for r in rows:
            d = dict(r)
            ts = d.get("created_at")
            if ts is not None:
                d["created_at"] = ts.isoformat()
            out.append(d)
        return out
    except Exception:
        logger.exception("list_gallery failed")
        return []
    finally:
        conn.close()
