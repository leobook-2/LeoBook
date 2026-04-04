# site_sport_scraper.py: Protocol for site + sport scrapers (Flashscore, football.com, …).
# Part of LeoBook Core — Scrapers
#
# Classes: SiteSportScraper
# Called by: Core/Scrapers/*_scraper.py adapters, orchestrators

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SiteSportScraper(Protocol):
    """Unified interface: one implementation per (site, sport) pair."""

    site: str
    sport: str

    async def extract_league_fixtures(self, browser_context: Any, league_id: str) -> int:
        """Return count of fixtures persisted for this league (0 if none/skipped)."""
        ...
