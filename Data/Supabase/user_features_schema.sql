-- user_features_schema.sql — Rule engines, stairway mirror, Football.com balance, RL jobs
-- Run in Supabase SQL Editor after core schema. Safe to re-run with IF NOT EXISTS.

-- ── user_rule_engines ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.user_rule_engines (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    description TEXT DEFAULT '',
    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_default BOOLEAN NOT NULL DEFAULT false,
    is_builtin_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_rule_engines_user ON public.user_rule_engines (user_id);

-- At most one default engine per user
CREATE UNIQUE INDEX IF NOT EXISTS uniq_user_rule_engines_one_default
    ON public.user_rule_engines (user_id)
    WHERE is_default = true;

-- ── user_stairway_state (mirror of SQLite stairway_state) ─────────────────
CREATE TABLE IF NOT EXISTS public.user_stairway_state (
    user_id TEXT PRIMARY KEY,
    current_step INTEGER NOT NULL DEFAULT 1,
    last_updated TIMESTAMPTZ,
    last_result TEXT,
    cycle_count INTEGER NOT NULL DEFAULT 0,
    week_bucket TEXT,
    week_cycles_completed INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── user_fb_balance (snapshot from worker / Ch2 P2) ─────────────────────────
CREATE TABLE IF NOT EXISTS public.user_fb_balance (
    user_id TEXT PRIMARY KEY,
    balance REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'NGN',
    source TEXT,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── rl_training_jobs ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.rl_training_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    rule_engine_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    train_season TEXT,
    phase INTEGER DEFAULT 1,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_rl_jobs_user ON public.rl_training_jobs (user_id);
CREATE INDEX IF NOT EXISTS idx_rl_jobs_status ON public.rl_training_jobs (status);

-- ── Row Level Security (authenticated users: own rows only) ────────────────
ALTER TABLE public.user_rule_engines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_stairway_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_fb_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rl_training_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_rule_engines_select_own" ON public.user_rule_engines
    FOR SELECT TO authenticated
    USING (auth.uid()::text = user_id);
CREATE POLICY "user_rule_engines_insert_own" ON public.user_rule_engines
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "user_rule_engines_update_own" ON public.user_rule_engines
    FOR UPDATE TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "user_rule_engines_delete_own" ON public.user_rule_engines
    FOR DELETE TO authenticated
    USING (auth.uid()::text = user_id);

CREATE POLICY "user_stairway_select_own" ON public.user_stairway_state
    FOR SELECT TO authenticated
    USING (auth.uid()::text = user_id);
CREATE POLICY "user_stairway_insert_own" ON public.user_stairway_state
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "user_stairway_update_own" ON public.user_stairway_state
    FOR UPDATE TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "user_fb_balance_select_own" ON public.user_fb_balance
    FOR SELECT TO authenticated
    USING (auth.uid()::text = user_id);
CREATE POLICY "user_fb_balance_insert_own" ON public.user_fb_balance
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "user_fb_balance_update_own" ON public.user_fb_balance
    FOR UPDATE TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "rl_jobs_select_own" ON public.rl_training_jobs
    FOR SELECT TO authenticated
    USING (auth.uid()::text = user_id);
CREATE POLICY "rl_jobs_insert_own" ON public.rl_training_jobs
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "rl_jobs_update_own" ON public.rl_training_jobs
    FOR UPDATE TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

-- service_role: full access (daemon / admin)
CREATE POLICY "service_role user_rule_engines" ON public.user_rule_engines
    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role user_stairway_state" ON public.user_stairway_state
    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role user_fb_balance" ON public.user_fb_balance
    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role rl_training_jobs" ON public.rl_training_jobs
    FOR ALL TO service_role USING (true) WITH CHECK (true);
