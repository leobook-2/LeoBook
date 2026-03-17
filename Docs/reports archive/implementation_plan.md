# Prediction Team Misplacement — Root Cause & Fix Plan

## Audit Results (live DB scan, 2026-03-17)

| Metric | Count | Rate |
|--------|-------|------|
| Schedules checked (vs match_link) | 5,000 | — |
| Team-ID mismatches | **0** | **0%** |
| Prediction home names mismatching schedule | **2,272 / 3,000** | **75.7%** |
| Prediction away names mismatching schedule | **2,249 / 3,000** | **75.0%** |
| Confirmed home↔away SWAPS | **464 / 3,000** | **15.5%** |
| `p.home_team == teams.name` | 295 / 500 | 59% |
| `p.home_team == sched.home_team_name` | 123 / 500 | **24.6%** |

**The `home_team_id` / `away_team_id` are 100% correct in both [schedules](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/db_helpers.py#277-280) and [predictions](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#189-373).**  
The problem is entirely in the **team names**, not in ID assignment.

---

## Root Cause 1 — DOM order ≠ URL order (SWAPS)
**File:** [Modules/Flashscore/fs_league_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_extractor.py) → `EXTRACT_MATCHES_JS`

The JS extractor reads `home_team_name` from `s.home_participant` DOM selector and `home_team_id` from the match link URL. These two sources are **not always in sync**:
- URL: `fk-liepaja-nym30tD6/ogre-united-Iu5ZbGPT` → home is FK Liepaja (nym30tD6)
- DOM: `home_participant` element may render **away** team's name in the "home" slot on some Flashscore layouts (e.g. Club Friendly pages, postponed fixtures, re-ordered tables)

Result: `schedules.home_team_name = 'Ogre United'` but `schedules.home_team_id = nym30tD6` (FK Liepaja's ID).

**Fix:** After extracting from DOM, validate that `home_team_id` matches the first ID in the URL path. If they're swapped, swap the names too.

---

## Root Cause 2 — [get_weekly_fixtures](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#67-97) JOIN discards `home_team_name`
**File:** [Core/Intelligence/prediction_pipeline.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py) → [get_weekly_fixtures()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#67-97)

The pipeline JOINs `teams.name` to get team names:
```sql
SELECT h.name AS home_team_name, a.name AS away_team_name, s.*
FROM schedules s
LEFT JOIN teams h ON s.home_team_id = h.team_id
LEFT JOIN teams a ON s.away_team_id = a.team_id
```
`teams.name` for a given [team_id](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#599-608) is **the name from the most recent upsert** — which may be from a completely different league context where the team has a different registered name (e.g. `nym30tD6` was last upserted as 'JFK Ventspils' in one league, is 'FK Liepaja' in another).

`schedules.home_team_name` (stored directly at scrape time) is the most reliable name for that specific fixture.

**Fix:** Use `schedules.home_team_name` / `schedules.away_team_name` directly. Stop over-writing with `teams.name`.

---

## Root Cause 3 — `teams.name` polluted by multi-league upserts
**File:** [Data/Access/league_db.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py) → [upsert_team()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#485-597)

Every league scrape does [upsert_team({team_id, name})](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#485-597) — name is from that league's DOM. A team playing in 5 leagues gets its `teams.name` overwritten 5 times with potentially different transliterations or aliases.

**Fix:** [upsert_team()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#485-597) should NOT overwrite `teams.name` if a name already exists (use `COALESCE(teams.name, excluded.name)` not `COALESCE(excluded.name, teams.name)`). The first-ever ingested name is most likely the canonical one from the team's home league.

---

## Proposed Changes

### Component 1 — JS Extractor (critical)

#### [MODIFY] [fs_league_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_extractor.py)

In `EXTRACT_MATCHES_JS`, after extracting `homeName`, `awayName`, `homeTeamId`, `awayTeamId` from both DOM and URL, add a validation block:

```js
// ROOT CAUSE 1 FIX: Validate DOM vs URL order. URL is canonical.
// If the IDs are swapped vs what the URL says, swap the names too.
if (mLink && mLink.includes('/match/football/')) {
    const parts = mLink.replace(/^.*\/match\/football\//, '').split('/').filter(p => p && !p.startsWith('?'));
    if (parts.length >= 2) {
        const urlHomeId = parts[0].substring(parts[0].lastIndexOf('-') + 1);
        const urlAwayId = parts[1].substring(parts[1].lastIndexOf('-') + 1);
        // If URL says homeId=X but DOM gave homeId=Y and Y==awayId, swap names
        if (urlHomeId && homeTeamId && urlHomeId !== homeTeamId && urlHomeId === awayTeamId) {
            [homeName, awayName] = [awayName, homeName];
            [homeTeamId, awayTeamId] = [awayTeamId, homeTeamId];
            [homeTeamUrl, awayTeamUrl] = [awayTeamUrl, homeTeamUrl];
        }
    }
}
```

---

### Component 2 — Prediction Pipeline (critical)

#### [MODIFY] [prediction_pipeline.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py)

**Change [get_weekly_fixtures()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#67-97)** — use `schedules.home_team_name` / `away_team_name` directly, fall back to `teams.name` only when stored name is NULL/empty:

```sql
-- BEFORE (wrong: teams.name overwrites schedules.home_team_name)
SELECT h.name AS home_team_name, a.name AS away_team_name, s.*
FROM schedules s
LEFT JOIN teams h ON s.home_team_id = h.team_id
LEFT JOIN teams a ON s.away_team_id = a.team_id

-- AFTER (correct: schedules.home_team_name is canonical, fall back to teams.name)
SELECT
    COALESCE(NULLIF(s.home_team_name,''), h.name) AS home_team_name,
    COALESCE(NULLIF(s.away_team_name,''), a.name) AS away_team_name,
    s.*
FROM schedules s
LEFT JOIN teams h ON s.home_team_id = h.team_id
LEFT JOIN teams a ON s.away_team_id = a.team_id
```

---

### Component 3 — Team upsert name protection

#### [MODIFY] [league_db.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py)

In [upsert_team()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#485-597) ON CONFLICT block, flip name priority so prior name is preserved:

```sql
-- BEFORE (bad: overwrites with new name)
name = COALESCE(excluded.name, teams.name),

-- AFTER (good: keep existing name if present)
name = COALESCE(NULLIF(teams.name,''), excluded.name),
```

---

### Component 4 — Integrity gate in [run_predictions()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#189-373)

#### [MODIFY] [prediction_pipeline.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py)

Before saving a prediction, validate team names don't look like they're from a different fixture:
```python
# Integrity check: if match_link exists, verify home/away IDs match URL
def _validate_home_away_from_link(fixture: Dict) -> bool:
    link = fixture.get('match_link', '')
    m = re.search(r'/match/football/([^/]+)/([^/]+)/', link)
    if not m: return True  # No link to validate against
    url_h_id = m.group(1).rsplit('-', 1)[-1]
    url_a_id = m.group(2).rsplit('-', 1)[-1]
    db_h_id = fixture.get('home_team_id', '')
    db_a_id = fixture.get('away_team_id', '')
    if url_h_id and db_h_id and url_h_id != db_h_id:
        return False
    return True
```
Log a warning and skip predictions where integrity check fails.

---

### Component 5 — Backfill script for existing schedules

Fix existing schedules rows by re-validating their stored names against match_link IDs:

```python
# Query schedules where home_team_id matches away URL segment (swapped rows)
# Swap home_team_name <-> away_team_name, home_team_id <-> away_team_id, etc.
# Run once as a one-off migration script (Scripts/fix_swapped_schedules.py)
```

---

## Verification Plan

### 1. Before/after swap count
```powershell
python Scripts/quantify_misplacement.py
# Expected after fix: confirmed_swaps drops from 464 to ~0
```

### 2. Prediction name accuracy check
```powershell
python Scripts/deepdive_misplacement.py
# Expected: p.home_team == sched.home_team_name rises from 24.6% to ~95%+
```

### 3. Full pipeline test
```powershell
python Leo.py --predict-only --date 2026-03-17
# Watch for [Integrity] WARNING lines — count should be ~0
```

> [!IMPORTANT]
> Component 3 ([league_db.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py) name protection) only affects future scrapes.
> Component 5 (backfill) is needed to correct existing poisoned schedule rows.
> Run the backfill script BEFORE the next prediction cycle.

> [!WARNING]
> The `teams.name` flip in Component 3 will freeze team names to whoever was scraped first.
> This is correct behavior — Flashscore team names in their home league are canonical.
> If a team is renamed, the [teams](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#229-300) table will need a manual update.
