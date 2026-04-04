# fs_flashscore_scraper.py: Flashscore adapter implementing SiteSportScraper.
# Part of LeoBook Core — Scrapers
#
# Classes: FlashscoreSiteScraper
# Called by: enrichment orchestrators (optional wiring)

import sqlite3
from typing import Optional

from Data.Access.league_db import init_db
from Modules.Flashscore.fs_league_tab import enrich_single_league


class FlashscoreSiteScraper:
    """Delegates to fs_league_tab.enrich_single_league for SQLite-backed leagues."""

    site = "flashscore"
    sport: str

    def __init__(self, sport: str = "football") -> None:
        self.sport = sport

    async def extract_league_fixtures(self, browser_context, league_id: str) -> int:
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = init_db()
            row = conn.execute(
                "SELECT league_id, name, url, country_code, continent FROM leagues WHERE league_id = ?",
                (league_id,),
            ).fetchone()
            if not row:
                return 0
            lg = dict(row)
            await enrich_single_league(browser_context, lg, conn, 1, 1)
            n = conn.execute(
                "SELECT COUNT(*) FROM schedules WHERE league_id = ?", (league_id,)
            ).fetchone()[0]
            return int(n)
        except Exception:
            return 0
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
