# fb_football_scraper.py: football.com football adapter implementing SiteSportScraper.
# Part of LeoBook Core — Scrapers
#
# Classes: FootballComFootballScraper
# Called by: orchestrators (optional wiring)

import json
import os

from Data.Access.db_helpers import save_site_matches
from Data.Access.league_db import LEAGUES_JSON_PATH, get_fb_url_for_league, init_db
from Modules.FootballCom.extractor import extract_league_matches, validate_match_data


def _entry_for_league(league_id: str) -> dict:
    path = LEAGUES_JSON_PATH
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for row in data:
            if row.get("league_id") == league_id:
                return row
    except Exception:
        pass
    return {}


class FootballComFootballScraper:
    site = "football.com"
    sport = "football"

    async def extract_league_fixtures(self, browser_context, league_id: str) -> int:
        conn = init_db()
        try:
            fb_url = get_fb_url_for_league(conn, league_id)
            entry = _entry_for_league(league_id)
            league_name = entry.get("fb_league_name") or entry.get("name") or ""
            if not fb_url or not league_name:
                return 0
        finally:
            conn.close()

        page = await browser_context.new_page()
        try:
            raw = await extract_league_matches(
                page,
                target_league_name=league_name,
                fb_url=fb_url,
            )
            if raw:
                raw = await validate_match_data(raw)
            if not raw:
                return 0
            normalized = [{
                "home": m.get("home", ""),
                "away": m.get("away", ""),
                "date": m.get("date", "Unknown"),
                "time": m.get("time", "Unknown"),
                "league": league_name,
                "url": m.get("url", ""),
                "status": m.get("status", ""),
                "score": "N/A",
            } for m in raw]
            save_site_matches(normalized)
            return len(normalized)
        finally:
            try:
                await page.close()
            except Exception:
                pass
