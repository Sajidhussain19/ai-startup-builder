import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "llm_usage.db"


def _db_path() -> Path:
    return Path(os.getenv("LLM_USAGE_DB_PATH", str(DEFAULT_DB_PATH)))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_usage_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                model TEXT NOT NULL,
                fallback_used INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                error TEXT,
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                input_cost_usd REAL NOT NULL DEFAULT 0,
                output_cost_usd REAL NOT NULL DEFAULT 0,
                total_cost_usd REAL NOT NULL DEFAULT 0,
                latency_ms INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_created_at ON llm_usage(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_agent_name ON llm_usage(agent_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_model ON llm_usage(model)")


def record_usage(
    *,
    agent_name: str,
    model: str,
    fallback_used: bool,
    status: str,
    error: Optional[str] = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    input_cost_usd: float = 0,
    output_cost_usd: float = 0,
    total_cost_usd: float = 0,
    latency_ms: int = 0,
) -> None:
    init_usage_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO llm_usage (
                created_at, agent_name, model, fallback_used, status, error,
                prompt_tokens, completion_tokens, total_tokens,
                input_cost_usd, output_cost_usd, total_cost_usd, latency_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                agent_name,
                model,
                1 if fallback_used else 0,
                status,
                error,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                input_cost_usd,
                output_cost_usd,
                total_cost_usd,
                latency_ms,
            ),
        )


def get_usage_summary() -> Dict[str, object]:
    init_usage_db()
    with _connect() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total_calls,
                COALESCE(SUM(total_tokens), 0) AS total_tokens,
                COALESCE(SUM(total_cost_usd), 0) AS total_cost_usd,
                COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                COALESCE(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END), 0) AS successful_calls,
                COALESCE(SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END), 0) AS failed_calls,
                COALESCE(SUM(fallback_used), 0) AS fallback_calls
            FROM llm_usage
            """
        ).fetchone()

        by_agent = conn.execute(
            """
            SELECT
                agent_name,
                COUNT(*) AS calls,
                COALESCE(SUM(total_tokens), 0) AS total_tokens,
                COALESCE(SUM(total_cost_usd), 0) AS total_cost_usd,
                COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                COALESCE(SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END), 0) AS failures
            FROM llm_usage
            GROUP BY agent_name
            ORDER BY total_cost_usd DESC
            """
        ).fetchall()

        by_model = conn.execute(
            """
            SELECT
                model,
                COUNT(*) AS calls,
                COALESCE(SUM(total_tokens), 0) AS total_tokens,
                COALESCE(SUM(total_cost_usd), 0) AS total_cost_usd,
                COALESCE(AVG(latency_ms), 0) AS avg_latency_ms
            FROM llm_usage
            GROUP BY model
            ORDER BY total_cost_usd DESC
            """
        ).fetchall()

    return {
        "totals": _row_to_dict(totals),
        "by_agent": [_row_to_dict(row) for row in by_agent],
        "by_model": [_row_to_dict(row) for row in by_model],
    }


def get_recent_usage(limit: int = 50) -> List[Dict[str, object]]:
    init_usage_db()
    safe_limit = max(1, min(limit, 200))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM llm_usage
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row: sqlite3.Row) -> Dict[str, object]:
    data = dict(row)
    for key in ("total_cost_usd", "input_cost_usd", "output_cost_usd"):
        if key in data:
            data[key] = round(float(data[key] or 0), 8)
    if "avg_latency_ms" in data:
        data["avg_latency_ms"] = round(float(data["avg_latency_ms"] or 0), 2)
    return data
