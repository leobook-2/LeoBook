# prologue_extraction.py: Prologue P2/P3 — Flashscore vs football.com extraction orchestration.
# Part of LeoBook Core — System
#
# Functions: prologue_p1_passed(), run_flashscore_prologue_refresh(),
#            run_football_com_prologue_phase0(), run_basketball_fb_prologue_phase0()
# Called by: Core/System/pipeline.py (run_prologue_p2, run_prologue_p3)

import json
import os
from typing import List, Optional, Tuple

from playwright.async_api import Playwright

from Core.System.data_readiness import check_leagues_ready
from Data.Access.league_db import LEAGUES_JSON_PATH, get_fb_url_for_league, init_db
from Data.Access.league_db_leagues import get_active_leagues, infer_flashscore_sport


def prologue_p1_passed() -> Tuple[bool, dict]:
    """True when Prologue P1 league/team gates are satisfied (same signal as check_leagues_ready)."""
    return check_leagues_ready()


def football_com_phase0_league_order(conn, days: int = 14) -> Optional[List[str]]:
    """
    Ordered league_ids for football.com Phase 0: 14-day active leagues with fb_url first,
    then remaining fb-mapped leagues. None if leagues.json is unusable (caller may sync all).
    """
    try:
        active = get_active_leagues(conn, days=days, sport="football")
    except Exception:
        return None

    priority: List[str] = []
    seen = set()
    for lg in active:
        lid = lg.get("league_id")
        if not lid or lid in seen:
            continue
        if get_fb_url_for_league(conn, lid):
            priority.append(lid)
            seen.add(lid)

    try:
        with open(LEAGUES_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        rows = data if isinstance(data, list) else []
        all_fb = [
            r["league_id"]
            for r in rows
            if r.get("fb_url")
            and r.get("league_id")
            and "/sport/football/" in (r.get("fb_url") or "")
            and infer_flashscore_sport(r.get("url")) == "football"
        ]
    except Exception:
        return priority or None

    rest = [x for x in all_fb if x not in seen]
    return priority + rest


async def run_flashscore_prologue_refresh(
    *,
    active_window_days: int = 14,
    priority_fb_mapped_first: bool = True,
    sports: Optional[List[str]] = None,
) -> None:
    """Prologue P2: Flashscore active-window refresh per sport (football + basketball)."""
    from Modules.Flashscore.fs_league_enricher import main as run_league_enricher

    sport_list = sports if sports is not None else ["football", "basketball"]
    for sp in sport_list:
        print(f"\n  [Prologue P2] Flashscore refresh — sport={sp}")
        await run_league_enricher(
            refresh=True,
            active_window_days=active_window_days,
            priority_fb_mapped_first=priority_fb_mapped_first,
            sport=sp,
        )


async def run_basketball_fb_prologue_phase0(
    playwright: Playwright,
    *,
    max_leagues: int = 40,
) -> None:
    """
    Prologue P3 (basketball): Discover leagues from the basketball schedule hub and
    sync fixtures via the same schedule extractor as football Phase 0.
    Order follows the hub page (schedule-first / active-first proxy).
    """
    import asyncio
    from Modules.FootballCom.fb_basketball_odds import extract_basketball_leagues_fb
    from Modules.FootballCom.extractor import extract_league_matches, validate_match_data
    from Data.Access.db_helpers import save_site_matches

    print("\n" + "=" * 60)
    print("  PROLOGUE P3 (basketball): football.com schedule discovery")
    print("=" * 60)

    is_headless = os.getenv("CODESPACES") == "true" or (
        os.name != "nt" and not os.environ.get("DISPLAY")
    )
    from Core.Utils.constants import FB_MOBILE_USER_AGENT, FB_MOBILE_VIEWPORT

    browser = await playwright.chromium.launch(headless=is_headless)
    try:
        context = await browser.new_context(
            user_agent=FB_MOBILE_USER_AGENT,
            viewport=FB_MOBILE_VIEWPORT,
        )
        page = await context.new_page()
        bb_leagues = await extract_basketball_leagues_fb(page)
        if not bb_leagues:
            print("  [BB Phase0] No basketball leagues discovered; skipping.")
            return

        total_saved = 0
        for lg in bb_leagues[:max_leagues]:
            name = lg.get("name") or ""
            fb_url = lg.get("url") or ""
            if not fb_url:
                continue
            try:
                raw = await extract_league_matches(
                    page,
                    target_league_name=name,
                    fb_url=fb_url,
                )
                if raw:
                    raw = await validate_match_data(raw)
                if not raw:
                    print(f"    ! {name}: no fixtures")
                    continue
                normalized = [
                    {
                        "home": m.get("home", ""),
                        "away": m.get("away", ""),
                        "date": m.get("date", "Unknown"),
                        "time": m.get("time", "Unknown"),
                        "league": name,
                        "url": m.get("url", ""),
                        "status": m.get("status", ""),
                        "score": "N/A",
                    }
                    for m in raw
                ]
                save_site_matches(normalized)
                total_saved += len(normalized)
                print(f"    ✓ {name}: {len(normalized)} fixtures saved.")
            except Exception as e:
                print(f"    ! {name}: {e}")
            await asyncio.sleep(0.15)

        print(f"  [BB Phase0] Done. Fixtures saved this pass: {total_saved}")
    finally:
        await browser.close()


async def run_football_com_prologue_phase0(playwright: Playwright) -> None:
    """
    Prologue P3: football.com calendar / fixture discovery for mapped football leagues
    (Phase 0 — no login), then basketball hub pass. Priority: 14-day active + fb_url first.
    """
    from Modules.FootballCom.fb_phase0 import run_league_calendar_fixtures_sync

    conn = init_db()
    try:
        league_ids = football_com_phase0_league_order(conn, days=14)
    finally:
        conn.close()

    leagues_path = LEAGUES_JSON_PATH
    if not os.path.isfile(leagues_path):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        leagues_path = os.path.join(base, "Data", "Store", "leagues.json")

    await run_league_calendar_fixtures_sync(
        playwright,
        leagues_json_path=leagues_path,
        league_ids=league_ids,
    )
    await run_basketball_fb_prologue_phase0(playwright)
