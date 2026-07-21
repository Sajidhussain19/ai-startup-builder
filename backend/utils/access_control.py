import hmac
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, Request


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "access_control.db"


def _db_path() -> Path:
    return Path(os.getenv("ACCESS_CONTROL_DB_PATH", str(DEFAULT_DB_PATH)))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_access_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_usage (
                usage_date TEXT NOT NULL,
                identity TEXT NOT NULL,
                units INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (usage_date, identity)
            )
            """
        )


def require_app_access(request: Request) -> None:
    expected_token = os.getenv("APP_ACCESS_TOKEN", "")
    if not expected_token:
        return

    provided_token = request.headers.get("x-app-token", "")
    if not hmac.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Valid app access token required.")


def require_admin_access(request: Request) -> None:
    expected_token = os.getenv("ADMIN_API_TOKEN", os.getenv("APP_ACCESS_TOKEN", ""))
    if not expected_token:
        return

    provided_token = request.headers.get("x-admin-token", request.headers.get("x-app-token", ""))
    if not hmac.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Valid admin token required.")


def enforce_daily_quota(request: Request, units: int = 1) -> Tuple[int, int]:
    limit = int(os.getenv("DAILY_GENERATION_LIMIT", "20"))
    if limit <= 0:
        return 0, 0

    init_access_db()
    identity = _request_identity(request)
    today = datetime.now(timezone.utc).date().isoformat()
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        row = conn.execute(
            "SELECT units FROM daily_usage WHERE usage_date = ? AND identity = ?",
            (today, identity),
        ).fetchone()
        used = int(row["units"]) if row else 0
        if used + units > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily generation limit reached. Limit: {limit} units per day.",
            )

        if row:
            conn.execute(
                "UPDATE daily_usage SET units = ?, updated_at = ? WHERE usage_date = ? AND identity = ?",
                (used + units, now, today, identity),
            )
        else:
            conn.execute(
                "INSERT INTO daily_usage (usage_date, identity, units, updated_at) VALUES (?, ?, ?, ?)",
                (today, identity, units, now),
            )

    return used + units, limit


def _request_identity(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
