-- LeoBook Supabase RLS Fix
-- Run this in the Supabase SQL Editor to allow the Flutter app to read data.

-- 1. Schedules
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "schedules_select_public" ON public.schedules;
CREATE POLICY "schedules_select_public" ON public.schedules
FOR SELECT TO anon, authenticated
USING (true);

-- 2. Predictions
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "predictions_select_public" ON public.predictions;
CREATE POLICY "predictions_select_public" ON public.predictions
FOR SELECT TO anon, authenticated
USING (true);

-- 3. Leagues
ALTER TABLE public.leagues ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "leagues_select_public" ON public.leagues;
CREATE POLICY "leagues_select_public" ON public.leagues
FOR SELECT TO anon, authenticated
USING (true);

-- 4. Teams
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "teams_select_public" ON public.teams;
CREATE POLICY "teams_select_public" ON public.teams
FOR SELECT TO anon, authenticated
USING (true);

-- 5. Live Scores
ALTER TABLE public.live_scores ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "live_scores_select_public" ON public.live_scores;
CREATE POLICY "live_scores_select_public" ON public.live_scores
FOR SELECT TO anon, authenticated
USING (true);

-- 6. Match Odds
ALTER TABLE public.match_odds ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "match_odds_select_public" ON public.match_odds;
CREATE POLICY "match_odds_select_public" ON public.match_odds
FOR SELECT TO anon, authenticated
USING (true);

-- 7. Statistics (fb_matches)
ALTER TABLE public.fb_matches ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "fb_matches_select_public" ON public.fb_matches;
CREATE POLICY "fb_matches_select_public" ON public.fb_matches
FOR SELECT TO anon, authenticated
USING (true);

-- 8. Profiles (Optional, if used)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "profiles_select_public" ON public.profiles;
CREATE POLICY "profiles_select_public" ON public.profiles
FOR SELECT TO anon, authenticated
USING (true);
