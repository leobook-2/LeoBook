# sync_schema.py: Supabase table schema DDL, column mappings, and sync config.
# Part of LeoBook Data — Access Layer
# Authoritative source for: TABLE_CONFIG, SUPABASE_SCHEMA, _ALLOWED_COLS, _COL_REMAP
# IMPORTANT: Column names here must exactly match sync_manager.SUPABASE_SCHEMA —
# they control what _ALLOWED_COLS accepts during push operations.

import re
from typing import Dict

# SQLite table -> Supabase table mapping
TABLE_CONFIG = {
    'predictions':      {'local_table': 'predictions',      'remote_table': 'predictions',      'key': 'fixture_id'},
    'schedules':        {'local_table': 'schedules',        'remote_table': 'schedules',        'key': 'fixture_id'},
    'teams':            {'local_table': 'teams',            'remote_table': 'teams',            'key': 'team_id'},
    'leagues':          {'local_table': 'leagues',          'remote_table': 'leagues',          'key': 'league_id'},
    'fb_matches':       {'local_table': 'fb_matches',       'remote_table': 'fb_matches',       'key': 'site_match_id'},
    'profiles':         {'local_table': 'profiles',         'remote_table': 'profiles',         'key': 'id'},
    'custom_rules':     {'local_table': 'custom_rules',     'remote_table': 'custom_rules',     'key': 'id'},
    'rule_executions':  {'local_table': 'rule_executions',  'remote_table': 'rule_executions',  'key': 'id'},
    'accuracy_reports': {'local_table': 'accuracy_reports', 'remote_table': 'accuracy_reports', 'key': 'report_id'},
    'audit_log':        {'local_table': 'audit_log',        'remote_table': 'audit_log',        'key': 'id'},
    'live_scores':      {'local_table': 'live_scores',      'remote_table': 'live_scores',      'key': 'fixture_id'},
    'countries':        {'local_table': 'countries',        'remote_table': 'countries',        'key': 'code'},
    'match_odds':       {'local_table': 'match_odds',       'remote_table': 'match_odds',       'key': 'fixture_id,market_id,exact_outcome,line'},
}

# ── Supabase auto-provisioning DDL ─────────────────────────────────────────
SUPABASE_SCHEMA = {
    'predictions': """
        CREATE TABLE IF NOT EXISTS public.predictions (
            fixture_id TEXT PRIMARY KEY,
            date TEXT, match_time TEXT, region_league TEXT,
            home_team TEXT, away_team TEXT, home_team_id TEXT, away_team_id TEXT,
            prediction TEXT, confidence TEXT, reason TEXT,
            xg_home REAL, xg_away REAL, btts TEXT, over_2_5 TEXT,
            best_score TEXT, top_scores TEXT,
            home_form_n INTEGER, away_form_n INTEGER,
            home_tags TEXT, away_tags TEXT, h2h_tags TEXT, standings_tags TEXT,
            h2h_count INTEGER, actual_score TEXT, outcome_correct TEXT,
            status TEXT DEFAULT 'pending', match_link TEXT, odds TEXT,
            market_reliability_score REAL, home_crest_url TEXT, away_crest_url TEXT,
            recommendation_score REAL, h2h_fixture_ids JSONB, form_fixture_ids JSONB,
            standings_snapshot JSONB, league_stage TEXT, generated_at TEXT,
            home_score TEXT, away_score TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'schedules': """
        CREATE TABLE IF NOT EXISTS public.schedules (
            fixture_id TEXT PRIMARY KEY,
            date TEXT, match_time TEXT, league_id TEXT,
            home_team_id TEXT, home_team TEXT, away_team_id TEXT, away_team TEXT,
            home_score INTEGER, away_score INTEGER, extra JSONB,
            league_stage TEXT, match_status TEXT, season TEXT,
            home_crest TEXT, away_crest TEXT, match_link TEXT,
            region_league TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'teams': """
        CREATE TABLE IF NOT EXISTS public.teams (
            team_id TEXT PRIMARY KEY,
            name TEXT NOT NULL, league_ids JSONB, crest TEXT,
            country_code TEXT, url TEXT,
            city TEXT, stadium TEXT,
            other_names TEXT, abbreviations TEXT, search_terms TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'leagues': """
        CREATE TABLE IF NOT EXISTS public.leagues (
            league_id TEXT PRIMARY KEY,
            fs_league_id TEXT, country_code TEXT, continent TEXT,
            name TEXT NOT NULL, crest TEXT, current_season TEXT,
            url TEXT, region_flag TEXT,
            other_names TEXT, abbreviations TEXT, search_terms TEXT,
            level TEXT, season_format TEXT,
            date_updated TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'audit_log': """
        CREATE TABLE IF NOT EXISTS public.audit_log (
            id TEXT PRIMARY KEY,
            timestamp TEXT, event_type TEXT, description TEXT,
            balance_before REAL, balance_after REAL, stake REAL, status TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'fb_matches': """
        CREATE TABLE IF NOT EXISTS public.fb_matches (
            site_match_id TEXT PRIMARY KEY,
            date TEXT, match_time TEXT, home_team TEXT, away_team TEXT,
            league TEXT, url TEXT, last_extracted TEXT, fixture_id TEXT,
            matched TEXT, odds TEXT, booking_status TEXT, booking_details TEXT,
            booking_code TEXT, booking_url TEXT, status TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
        # NOTE: Supabase column renamed from 'time' → 'match_time' on 2026-03-16.
        # Run once in Supabase SQL editor after deploying this change:
        #   ALTER TABLE public.fb_matches RENAME COLUMN time TO match_time;
    'live_scores': """
        CREATE TABLE IF NOT EXISTS public.live_scores (
            fixture_id TEXT PRIMARY KEY,
            home_team TEXT, away_team TEXT,
            home_score TEXT, away_score TEXT, minute TEXT,
            status TEXT, region_league TEXT, match_link TEXT, timestamp TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'accuracy_reports': """
        CREATE TABLE IF NOT EXISTS public.accuracy_reports (
            report_id TEXT PRIMARY KEY,
            timestamp TEXT, volume INTEGER, win_rate REAL,
            return_pct REAL, period TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'countries': """
        CREATE TABLE IF NOT EXISTS public.countries (
            code TEXT PRIMARY KEY,
            name TEXT, continent TEXT, capital TEXT,
            flag_1x1 TEXT, flag_4x3 TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'profiles': """
        CREATE TABLE IF NOT EXISTS public.profiles (
            id TEXT PRIMARY KEY,
            email TEXT, username TEXT, full_name TEXT,
            avatar_url TEXT, tier TEXT, credits REAL,
            created_at TEXT, updated_at TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'custom_rules': """
        CREATE TABLE IF NOT EXISTS public.custom_rules (
            id TEXT PRIMARY KEY,
            user_id TEXT, name TEXT, description TEXT,
            is_active INTEGER, logic TEXT, priority INTEGER,
            created_at TEXT, updated_at TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'rule_executions': """
        CREATE TABLE IF NOT EXISTS public.rule_executions (
            id TEXT PRIMARY KEY,
            rule_id TEXT, fixture_id TEXT, user_id TEXT,
            result TEXT, executed_at TEXT,
            last_updated TIMESTAMPTZ DEFAULT now()
        );""",
    'match_odds': """
        CREATE TABLE IF NOT EXISTS public.match_odds (
            fixture_id TEXT,
            site_match_id TEXT,
            market_id TEXT,
            base_market TEXT,
            category TEXT,
            exact_outcome TEXT,
            line TEXT,
            odds_value REAL,
            likelihood_pct INTEGER,
            rank_in_list INTEGER,
            extracted_at TEXT,
            last_updated TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (fixture_id, market_id, exact_outcome, line)
        );""",
}

# ── Derived: allowed columns per remote table (parsed from SUPABASE_SCHEMA DDL) ──
_ALLOWED_COLS: Dict[str, set] = {}
for _tbl, _ddl in SUPABASE_SCHEMA.items():
    _cols = set(re.findall(r'\b([a-z_][a-z0-9_]*)\s+(?:TEXT|INTEGER|REAL|JSONB|TIMESTAMPTZ|BOOLEAN)', _ddl, re.IGNORECASE))
    _cols.discard('TABLE')
    _cols.discard('NOT')
    _cols.discard('IF')
    _cols.discard('EXISTS')
    _cols.discard('DEFAULT')
    _ALLOWED_COLS[_tbl] = _cols

# Column remaps: local name → remote name (applied before schema filtering)
_COL_REMAP = {
    'time':           'match_time',
    'over_2.5':       'over_2_5',
    'country':        'country_code',
    'team_name':      'name',
    'home_team_name': 'home_team',
    'away_team_name': 'away_team',
}

# ── Per-table batch sizes ─────────────────────────────────────────────────────
_BATCH_SIZES: Dict[str, int] = {
    'schedules':   500,
    'match_odds':  1000,
    'predictions': 200,   # 1969-row single upsert → Supabase 57014 timeout. Chunked at 200.
    'default':     2000,
}

# ── Matching Engine v1.2 — full idempotent SQL (STEP 9 from bootstrap) ────────
# Used by any bootstrap/provision routine to install the SQL matching engine
# on a fresh or existing Supabase project. Safe to re-run (CREATE OR REPLACE).
# Run via:
#   supabase.rpc('exec_sql', {'query': MATCHING_ENGINE_SQL})
# or paste directly in Supabase SQL Editor.
# v1.2 adds: normalize_team_name(), fb_match_candidates view,
#             match_fb_to_schedule(), auto_match_fb_matches(),
#             trg_auto_match_fb_matches trigger, performance indexes.
MATCHING_ENGINE_SQL = """
-- =============================================================================
-- LEOBOOK Team Matching Engine v1.2  (2026-03-17) — STEP 9 bootstrap block
-- Safe to re-run: CREATE OR REPLACE / IF NOT EXISTS throughout.
-- =============================================================================

-- 9a: Name normalizer
CREATE OR REPLACE FUNCTION public.normalize_team_name(raw TEXT)
RETURNS TEXT LANGUAGE sql IMMUTABLE STRICT AS $$
  SELECT TRIM(
           REGEXP_REPLACE(
             REGEXP_REPLACE(
               LOWER(COALESCE(raw, '')),
               '\\m(fc|cf|sc|ac|bk|sk|fk|if|afc|bfc|sfc|united|city|town|rovers|wanderers|athletic|albion|county)\\M',
               '', 'gi'
             ),
             '[^a-z0-9]+', ' ', 'g'
           )
         )
$$;
GRANT EXECUTE ON FUNCTION public.normalize_team_name(TEXT) TO service_role, anon, authenticated;

-- 9b: Candidate view (fb_matches x schedules with confidence score)
CREATE OR REPLACE VIEW public.fb_match_candidates AS
SELECT
    fb.site_match_id,
    fb.date AS fb_date, fb.match_time AS fb_time,
    fb.home_team AS fb_home, fb.away_team AS fb_away,
    fb.league AS fb_league, fb.url AS fb_url,
    s.fixture_id,
    s.date AS s_date, s.match_time AS s_time,
    s.home_team AS s_home, s.away_team AS s_away,
    s.home_team_id, s.away_team_id, s.league_id, s.region_league,
    CASE
        WHEN public.normalize_team_name(fb.home_team) = public.normalize_team_name(s.home_team)
         AND public.normalize_team_name(fb.away_team) = public.normalize_team_name(s.away_team)
        THEN 100
        WHEN (
            public.normalize_team_name(fb.home_team) LIKE '%' || public.normalize_team_name(s.home_team) || '%'
            OR public.normalize_team_name(s.home_team) LIKE '%' || public.normalize_team_name(fb.home_team) || '%'
        ) AND (
            public.normalize_team_name(fb.away_team) LIKE '%' || public.normalize_team_name(s.away_team) || '%'
            OR public.normalize_team_name(s.away_team) LIKE '%' || public.normalize_team_name(fb.away_team) || '%'
        ) THEN 88
        ELSE 0
    END AS confidence
FROM public.fb_matches fb
CROSS JOIN public.schedules s
WHERE fb.date IS NOT NULL AND s.date IS NOT NULL
  AND ABS(EXTRACT(EPOCH FROM (fb.date::DATE - s.date::DATE)) / 86400) <= 1
  AND (fb.fixture_id IS NULL OR fb.matched IS NULL OR fb.matched = 'false')
  AND (
    public.normalize_team_name(fb.home_team) LIKE '%' || public.normalize_team_name(s.home_team) || '%'
    OR public.normalize_team_name(s.home_team) LIKE '%' || public.normalize_team_name(fb.home_team) || '%'
  );
GRANT SELECT ON public.fb_match_candidates TO anon, authenticated, service_role;

-- 9c: Per-row resolver (callable from Python via Supabase RPC)
CREATE OR REPLACE FUNCTION public.match_fb_to_schedule(p_site_match_id TEXT)
RETURNS TABLE(fixture_id TEXT, confidence INTEGER, home_team_id TEXT, away_team_id TEXT,
              s_home TEXT, s_away TEXT, s_date TEXT, s_time TEXT)
LANGUAGE sql STABLE AS $$
    SELECT c.fixture_id, c.confidence, c.home_team_id, c.away_team_id,
           c.s_home, c.s_away, c.s_date, c.s_time
    FROM public.fb_match_candidates c
    WHERE c.site_match_id = p_site_match_id AND c.confidence > 0
    ORDER BY c.confidence DESC, c.s_date ASC LIMIT 1;
$$;
GRANT EXECUTE ON FUNCTION public.match_fb_to_schedule(TEXT) TO service_role, anon, authenticated;

-- 9d: Batch resolver (runs all unmatched fb_matches, returns count)
CREATE OR REPLACE FUNCTION public.auto_match_fb_matches()
RETURNS INTEGER LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE matched_count INTEGER := 0; rec RECORD;
BEGIN
    FOR rec IN
        SELECT DISTINCT ON (site_match_id) site_match_id, fixture_id AS resolved_fixture_id, confidence
        FROM public.fb_match_candidates WHERE confidence >= 88
        ORDER BY site_match_id, confidence DESC
    LOOP
        UPDATE public.fb_matches
        SET fixture_id = rec.resolved_fixture_id, matched = 'sql_v1.2', last_updated = NOW()
        WHERE site_match_id = rec.site_match_id AND (fixture_id IS NULL OR fixture_id = '');
        IF FOUND THEN matched_count := matched_count + 1; END IF;
    END LOOP;
    RETURN matched_count;
END;
$$;
GRANT EXECUTE ON FUNCTION public.auto_match_fb_matches() TO service_role;

-- 9e: Per-row trigger (auto-matches each INSERT/UPDATE)
CREATE OR REPLACE FUNCTION public.trg_fn_auto_match_fb()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE best RECORD;
BEGIN
    IF NEW.fixture_id IS NOT NULL AND NEW.fixture_id <> '' THEN RETURN NEW; END IF;
    SELECT fixture_id, confidence INTO best FROM public.match_fb_to_schedule(NEW.site_match_id) LIMIT 1;
    IF FOUND AND best.confidence >= 88 THEN
        NEW.fixture_id := best.fixture_id; NEW.matched := 'sql_v1.2'; NEW.last_updated := NOW();
    END IF;
    RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trg_auto_match_fb_matches ON public.fb_matches;
CREATE TRIGGER trg_auto_match_fb_matches
    BEFORE INSERT OR UPDATE OF home_team, away_team, date ON public.fb_matches
    FOR EACH ROW EXECUTE FUNCTION public.trg_fn_auto_match_fb();

-- 9f: Performance indexes
CREATE INDEX IF NOT EXISTS idx_fb_matches_unresolved ON public.fb_matches (date)
    WHERE fixture_id IS NULL OR fixture_id = '';
CREATE INDEX IF NOT EXISTS idx_schedules_date_home_away ON public.schedules (date, home_team, away_team);
CREATE INDEX IF NOT EXISTS idx_schedules_date ON public.schedules (date);
"""

# Note: computed_standings VIEW is NOT in SUPABASE_SCHEMA because it is not
# a synced table — it is a Postgres VIEW defined in the bootstrap SQL and
# queried directly by the Flutter app and Python backend.
# It is re-created by SUPABASE_SETUP.md STEP 6 (and Part 3B upgrade path).

__all__ = [
    "TABLE_CONFIG",
    "SUPABASE_SCHEMA",
    "_ALLOWED_COLS",
    "_COL_REMAP",
    "_BATCH_SIZES",
    "MATCHING_ENGINE_SQL",
]
