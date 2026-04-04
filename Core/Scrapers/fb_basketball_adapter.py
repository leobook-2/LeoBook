# fb_basketball_adapter.py: football.com basketball adapter implementing SiteSportScraper.
# Part of LeoBook Core — Scrapers
#
# Classes: FootballComBasketballScraper
# Called by: orchestrators; full batch flow remains in fb_basketball_booker.py

from playwright.async_api import Page

from Modules.FootballCom.fb_basketball_odds import extract_basketball_match_odds


class FootballComBasketballScraper:
    """Per-match odds scrape; use [Modules/FootballCom/fb_basketball_booker] for full harvests."""

    site = "football.com"
    sport = "basketball"

    async def extract_league_fixtures(self, browser_context, league_id: str) -> int:
        """League_id may be a match URL path key — batch discovery uses fb_basketball_booker."""
        page: Page = await browser_context.new_page()
        try:
            if not league_id.startswith("http"):
                return 0
            result = await extract_basketball_match_odds(page, league_id)
            return 1 if result else 0
        finally:
            try:
                await page.close()
            except Exception:
                pass
