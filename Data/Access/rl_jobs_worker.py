# rl_jobs_worker.py: Consume rl_training_jobs from Supabase (service/sync client).
# Part of LeoBook Data — Access Layer
#
# Called by: Leo.py --process-rl-jobs

from __future__ import annotations

from typing import Any, Dict, Optional

from Data.Access.user_supabase_sync import fetch_queued_rl_job, update_rl_job_status


def process_rl_training_jobs_once() -> bool:
    """
    Pick the oldest queued job, mark running, run RLTrainer.train_from_fixtures
    with the requested rule_engine_id, then mark done or failed.
    """
    job: Optional[Dict[str, Any]] = fetch_queued_rl_job()
    if not job:
        print("  [RL Jobs] No queued jobs.")
        return False

    jid = str(job.get("id", ""))
    rule_engine_id = job.get("rule_engine_id") or "default"
    train_season = job.get("train_season") or "current"
    phase = int(job.get("phase") or 1)

    if isinstance(train_season, str) and train_season.isdigit():
        train_season = int(train_season)

    print(f"  [RL Jobs] Running job {jid} engine={rule_engine_id!r} season={train_season!r} phase={phase}")
    update_rl_job_status(jid, "running")

    try:
        from Core.Intelligence.rl.trainer import RLTrainer

        trainer = RLTrainer()
        if phase > 1:
            trainer.load()
        trainer.train_from_fixtures(
            phase=phase,
            cold=False,
            limit_days=None,
            resume=False,
            target_season=train_season,
            rule_engine_id=rule_engine_id,
        )
        update_rl_job_status(jid, "done")
        print("  [RL Jobs] Job completed successfully.")
        return True
    except Exception as e:
        update_rl_job_status(jid, "failed", error=str(e))
        print(f"  [RL Jobs] Job failed: {e}")
        raise
