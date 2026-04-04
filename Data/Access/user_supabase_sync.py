# user_supabase_sync.py: Push per-user stairway / Football.com balance to Supabase.
# Part of LeoBook Data — Access Layer
#
# Called by: Core/System/pipeline.py, Core/System/guardrails.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from Data.Access.league_db import get_connection
from Data.Access.supabase_client import get_supabase_client


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def push_stairway_snapshot(user_id: str) -> bool:
    """Upsert SQLite stairway_state row to public.user_stairway_state."""
    if not user_id:
        return False
    sb = get_supabase_client()
    if not sb:
        return False
    conn = get_connection()
    row = None
    try:
        row = conn.execute(
            "SELECT current_step, last_updated, last_result, cycle_count, "
            "week_bucket, week_cycles_completed FROM stairway_state WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    except Exception:
        try:
            row = conn.execute(
                "SELECT current_step, last_updated, last_result, cycle_count "
                "FROM stairway_state WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        except Exception:
            return False
    if not row:
        return False
    if len(row) >= 6:
        step, last_upd, last_res, cyc, week_b, week_cc = row[0], row[1], row[2], row[3], row[4], row[5]
    else:
        step, last_upd, last_res, cyc = row[0], row[1], row[2], row[3]
        week_b, week_cc = None, 0
    payload: Dict[str, Any] = {
        "user_id": user_id,
        "current_step": int(step or 1),
        "last_result": last_res,
        "cycle_count": int(cyc or 0),
        "week_bucket": week_b,
        "week_cycles_completed": int(week_cc or 0),
        "updated_at": _iso_now(),
    }
    if last_upd:
        try:
            payload["last_updated"] = last_upd if "T" in str(last_upd) else f"{last_upd}Z"
        except Exception:
            payload["last_updated"] = _iso_now()
    else:
        payload["last_updated"] = _iso_now()
    try:
        sb.table("user_stairway_state").upsert(payload, on_conflict="user_id").execute()
        return True
    except Exception as e:
        print(f"  [Sync] user_stairway_state upsert failed: {e}")
        return False


def push_fb_balance_snapshot(
    user_id: str,
    balance: float,
    source: str = "ch2_p2",
) -> bool:
    """Upsert Football.com balance to public.user_fb_balance."""
    if not user_id:
        return False
    sb = get_supabase_client()
    if not sb:
        return False
    payload = {
        "user_id": user_id,
        "balance": float(balance),
        "currency": "NGN",
        "source": source,
        "captured_at": _iso_now(),
    }
    try:
        sb.table("user_fb_balance").upsert(payload, on_conflict="user_id").execute()
        return True
    except Exception as e:
        print(f"  [Sync] user_fb_balance upsert failed: {e}")
        return False


def fetch_queued_rl_job() -> Optional[Dict[str, Any]]:
    """Return one queued RL job (oldest first), or None. Uses service/sync client."""
    sb = get_supabase_client()
    if not sb:
        return None
    try:
        res = (
            sb.table("rl_training_jobs")
            .select("*")
            .eq("status", "queued")
            .order("requested_at")
            .limit(1)
            .execute()
        )
        rows = getattr(res, "data", None) or []
        return rows[0] if rows else None
    except Exception:
        return None


def update_rl_job_status(
    job_id: str,
    status: str,
    error: Optional[str] = None,
) -> bool:
    sb = get_supabase_client()
    if not sb or not job_id:
        return False
    patch: Dict[str, Any] = {"status": status}
    now = _iso_now()
    if status == "running":
        patch["started_at"] = now
    if status in ("done", "failed"):
        patch["finished_at"] = now
    if error:
        patch["error"] = error[:8000] if error else None
    try:
        sb.table("rl_training_jobs").update(patch).eq("id", job_id).execute()
        return True
    except Exception as e:
        print(f"  [RL Jobs] status update failed: {e}")
        return False
