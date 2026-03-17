# LeoBook Codebase Health Report — v2026-03-17
**Analyst:** Antigravity Full Codebase Auditor  
**Latest commit:** `b5e4212` (fix: prediction team name misplacement, 2026-03-17)  
**Scope:** Fresh audit — all files read cold from disk.

---

## Executive Summary

| # | Area | Severity | Status |
|---|------|----------|--------|
| 1 | Supabase PGRST205 schema cache | 🔴 HIGH | [_ensure_remote_table](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_manager.py#59-80) uses missing `exec_sql` RPC |
| 2+7 | football.com odds = 0/1 outcomes | 🔴 HIGH | Collapsed accordion containers never clicked; no retry |
| 3 | Grok `grok-beta` dead | 🟠 MED | Hardcoded in 2 places; ping & call both fail |
| 4 | Gemini 403 farm | 🟡 LOW | Handler correct; ping model may not exist |
| 5 | Dumb-impatience hydration | 🟡 LOW | Early-exit logic present but weak "no games" detection |
| 6 | Scraping hydration fragility | 🟢 OK | `_scroll_to_load` + accordion-click already implemented |
| 12 | No retry on partial harvests | 🟠 MED | [_odds_worker](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py#154-204) has no per-match retry |

---

## Bug 1 — Supabase PGRST205 Schema Cache

**File:** [sync_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_manager.py) — [_ensure_remote_table()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_manager.py#59-80) (lines 59–79)

### Root Cause
```python
# Line 67 — calls exec_sql RPC that may not exist in Supabase schema:
self.supabase.rpc('exec_sql', {'query': ddl.strip()}).execute()
```
`exec_sql` is a custom Postgres function that must be manually created in Supabase. After a fresh environment or schema reset, this RPC is missing, so auto-create silently fails (exception is eaten on line 68–69). The table stays absent → all upserts get PGRST205 → entire sync skips.

**Affected tables:** [schedules](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/db_helpers.py#277-280), [teams](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#229-300), [leagues](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#466-479), `audit_log` (any table not yet provisioned).

### PGRST205 Flow
```
batch_upsert()
→ upsert() raises PGRST205
→ _ensure_remote_table() calls exec_sql RPC
→ exec_sql RPC missing → exception caught, returns False
→ raise batch_err (original PGRST205)
→ entire table sync aborted
```

### Fix
Replace `exec_sql` RPC path with direct Supabase `postgrest` DDL endpoint OR fallback to a silent "table exists" guard — if auto-create is impossible, skip this table and log a clear action item.

**Option A (recommended):** Drop [_ensure_remote_table](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_manager.py#59-80) silent auto-create; instead log a `[ACTION REQUIRED]` message with the DDL to run manually. The SUPABASE_SCHEMA DDL is already defined — just print it.

**Option B:** Replace `exec_sql` with `supabase.rpc('query', {'sql': ddl})` after ensuring the RPC is registered (add to Supabase migration).

**Trade-off:** Option A is safe + zero-dependency. Option B requires maintaining an RPC in two places.

---

## Bug 2 + 7 — Football.com Odds Harvest = 1 Outcome Total

### Sub-Bug 2a — Collapsed accordion containers never expanded

**File:** [odds_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/odds_extractor.py) — [extract()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/odds_extractor.py#104-244) (lines 104–244)

#### Root Cause
```python
# Line 128–130: scrolls until [data-market-id] elements are in DOM
containers_found = await _scroll_to_load(self.page, "[data-market-id]")

# Line 151–155: queries the container
container = await self.page.query_selector(f"[data-market-id='{market_id}']")
if not container: continue

# Line 162–165: scrolls container into view
await container.scroll_into_view_if_needed()

# Line 171: reads outcome rows
outcome_rows = await container.query_selector_all(".m-table-row")
```

football.com market containers are **accordion sections** — collapsed by default. Scrolling brings them into the DOM but doesn't expand them. `.m-table-row` elements within collapsed containers have `display: none` or zero computed height. `query_selector_all` returns them (they're in the DOM) but their `inner_text()` is empty → `name_el` or `odds_el` is None → `continue`.

**Evidence:** "1 outcome total" is exactly consistent with one market being already-expanded (e.g., Match Result) while all others are collapsed.

#### Fix (lines 160–165)
After `scroll_into_view_if_needed`, add accordion click:
```python
# Expand accordion if collapsed
try:
    is_collapsed = await container.evaluate(
        "(el) => el.classList.contains('collapsed') || "
        "el.getAttribute('aria-expanded') === 'false' || "
        "getComputedStyle(el.querySelector('.m-table-row') || el)"
        ".display === 'none'"
    )
    if is_collapsed:
        toggle = await container.query_selector(
            "[class*='accordion'], [class*='expand'], "
            "[class*='header'], [data-toggle]"
        )
        if toggle:
            await toggle.click()
            await asyncio.sleep(0.3)
        else:
            await container.click()  # click container itself to toggle
            await asyncio.sleep(0.3)
except Exception:
    pass
```

### Sub-Bug 7 — No retry on partial harvest

**File:** [fb_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py) — [_odds_worker()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py#154-204) (lines 154–203)

#### Root Cause
```python
# Line 177–181: single navigation attempt, no retry
await odds_page.goto(match_url, wait_until="domcontentloaded", timeout=25000)
await asyncio.sleep(1.5)
result = await extractor.extract(fixture_id, site_id)  # if this gets 0 outcomes, no retry
```
If [extract()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/odds_extractor.py#104-244) returns `outcomes_extracted=0` (collapsed containers), the worker returns that 0-result immediately. No retry, no re-navigation.

#### Fix
After `result = await extractor.extract(...)`, check `result.outcomes_extracted == 0` and retry up to 2 times with a page reload:
```python
for attempt in range(3):
    result = await extractor.extract(fixture_id, site_id)
    if result.outcomes_extracted > 0:
        break
    if attempt < 2:
        print(f"    [Odds] {fixture_id}: 0 outcomes, reloading (attempt {attempt+2}/3)...")
        await odds_page.reload(wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(2)
```

---

## Bug 3 — Grok `grok-beta` Dead

**Files:**
- [api_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/api_manager.py) — line **77**: `"model": "grok-beta"`
- [llm_health_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py) — line **62**: `GROK_MODEL = "grok-beta"`

### Root Cause
`grok-beta` was removed from the xAI API. Any call returns 404. The health ping (line 331) uses `GROK_MODEL = "grok-beta"` → ping fails → Grok marked inactive. All subsequent [grok_api_call()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/api_manager.py#16-114) also fail with 404 at line 77.

### Fix
Two-line change:
```python
# api_manager.py line 77:
"model": "grok-4.20-beta-0309-reasoning",

# llm_health_manager.py line 62:
GROK_MODEL = "grok-4.20-beta-0309-reasoning"
```

**Trade-off:** `grok-4.20-beta-0309-reasoning` is a fast-reasoning model — slightly higher latency than `grok-beta` for simple calls. If speed matters more, verify current available models via `GET https://api.x.ai/v1/models`.

---

## Bug 4 — Gemini Key Farm 403s

**File:** [llm_health_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py)

### Current State — CORRECT
[on_gemini_fatal_error()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py#258-274) (line 258–273) permanently removes 403 keys from both `_gemini_active` and `_gemini_keys`. The `_dead_keys` set prevents re-adding. This is correct behavior.

### Remaining Risk
[_ping_key()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py#375-398) using `PING_MODEL = "gemini-3.1-flash-lite-preview"` — if this model name is wrong (renamed by Google), ALL keys will return 404 → marked dead → Gemini pool emptied spuriously.

### Fix
Add model name validation in [_ping_key](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py#375-398): if response is 404, treat as `FAIL` (transient wrong model), not `FATAL` (bad key):
```python
# Current line 392-393:
if resp.status_code in (401, 403) or (resp.status_code == 400 and "INVALID_ARGUMENT" in resp.text):
    return "FATAL"
# Add:
if resp.status_code == 404:
    return "FAIL"  # Model not found — don't kill the key
```

---

## Bug 5 — Dumb-Impatience (Loading vs No-Matches)

**File:** [extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py) — [_activate_and_wait_for_matches()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py#23-98) (lines 23–97)

### Current State
Checks for `NO_DATA_SELECTORS` before AND after scroll. Phase 1 activates tabs, Phase 2 runs stability-polling scroll. This is essentially correct.

### Remaining Gap
The "no upcoming games" check (lines 44–55) runs on selectors that may not exist on tournament pages where the structure is different. If the page is still loading when the check runs, it returns False and exits early — treating "still loading" as "empty page".

### Fix
Add a minimum wait before the first empty-check:
```python
# After page.goto(), add in _activate_and_wait_for_matches():
await page.wait_for_load_state("networkidle", timeout=10000)  # wait up to 10s for network
```
Then re-check `NO_DATA_SELECTORS`. This prevents returning False during transient empty states.

---

## Bug 6 — Scraping Hydration & Scroll Fragility

**Files:** [extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py), [fs_league_hydration.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_hydration.py)

### Current State — MOSTLY OK ✅
`_scroll_to_load()` from [fs_league_hydration.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_hydration.py) is reused. Accordion click is already in the Global Schedule path (line 185–187). [_extract_matches_from_container](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py#208-331) correctly scopes queries.

### Remaining Gap
On tournament pages (is_tournament_page=True), **no accordion click happens** — [_activate_and_wait_for_matches](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py#23-98) scrolls but doesn't click accordions. The match cards on tournament pages don't need accordion clicks (they're flat cards), so this is OK for schedule extraction. For odds extraction (in [odds_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/odds_extractor.py)) — this is where the accordion click is missing (see Bug 2a above).

---

## Bug 12 — No Backoff/Retry on Partial Harvests

See **Sub-Bug 7** above. Additionally:

**File:** [fb_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py) — [run_odds_harvesting()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py#354-577) batch loop (lines 435–534)

### Gap
If an entire batch fails (`batch_outcomes == 0`), no retry is attempted for that batch. The checkpoint marks it complete. On next run, it skips that batch.

### Fix
Track batches with 0 outcomes and retry them:
```python
batch_outcomes = sum(r.outcomes_extracted for r in results if isinstance(r, OddsResult))
if batch_outcomes == 0 and batch_resolved:
    print(f"    [Batch {batch_num}] WARNING: 0 outcomes — will retry this batch next run")
    # Don't save checkpoint for this batch:
    _save_checkpoint(batch_idx)  # not batch_idx + 1
else:
    _save_checkpoint(batch_idx + 1)
```

---

## File Map — Changed vs Unchanged

| File | Lines Audited | Bugs Found | Action Required |
|------|--------------|------------|-----------------|
| [api_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/api_manager.py) | 1–301 | Bug 3 (line 77) | Change model name |
| [llm_health_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/llm_health_manager.py) | 1–401 | Bug 3 (line 62), Bug 4 (line 392) | 2 fixes |
| [odds_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/odds_extractor.py) | 1–244 | Bug 2a (line 162–171) | Add accordion click |
| [fb_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_manager.py) | 1–665 | Bug 7 (line 185), Bug 12 (line 534) | Retry + checkpoint fix |
| [extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/extractor.py) | 1–359 | Bug 5 (line 44) | Add networkidle wait |
| [sync_manager.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_manager.py) | 1–430 | Bug 1 (line 67) | Replace exec_sql RPC |
| [sync_schema.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/sync_schema.py) | 1–100 | None — schema correct | — |
| [fb_session.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/FootballCom/fb_session.py) | 1–99 | None — solid | — |
| [fs_league_extractor.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_extractor.py) | 1–433 | None after b5e4212 fix | — |
| [prediction_pipeline.py](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py) | 1–422 | None after b5e4212 fix | — |

---

## Supabase Schema Cache Status

Tables in scope and their provisioning risk:

| Table | DDL in SUPABASE_SCHEMA | Risk |
|-------|----------------------|------|
| [predictions](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Core/Intelligence/prediction_pipeline.py#194-378) | ✅ Yes | OK |
| [schedules](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/db_helpers.py#277-280) | ✅ Yes | OK |
| [teams](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#229-300) | ✅ Yes | OK |
| [leagues](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/league_db.py#466-479) | ✅ Yes | OK |
| `fb_matches` | ✅ Yes | ⚠️ Needs ALTER TABLE (time→match_time) |
| `audit_log` | ✅ Yes | OK |
| `live_scores` | ✅ Yes | OK |
| [match_odds](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/db_helpers.py#646-655) | ❓ Not in SUPABASE_SCHEMA | PGRST205 if missing |
| `paper_trades` | ❓ Not in SUPABASE_SCHEMA | PGRST205 if missing |
| `custom_rules` | ❓ Not in SUPABASE_SCHEMA | PGRST205 if missing |

**Action required for [match_odds](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Data/Access/db_helpers.py#646-655)** — this is the table odds are pushed to. If it doesn't exist in Supabase, every odds sync fails silently.

---

## Priority Fix Order

```
1. api_manager.py + llm_health_manager.py — grok-beta → grok-4.20-beta-0309-reasoning  [5min]
2. odds_extractor.py — accordion click before reading .m-table-row                     [20min]
3. fb_manager.py — retry when outcomes_extracted==0                                    [10min]
4. sync_manager.py — replace exec_sql with explicit user-facing DDL error              [15min]
5. extractor.py — networkidle wait before empty-check                                  [5min]
6. sync_schema.py — add match_odds + paper_trades DDL for auto-provisioning            [15min]
```

---

**Report complete. STATUS: SUCCESS**  
Ready for implementation prompt.
