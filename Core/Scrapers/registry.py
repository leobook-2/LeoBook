# registry.py: (site, sport) → scraper implementation registry.
# Part of LeoBook Core — Scrapers
#
# Functions: get_scraper(), list_registered_scraper_keys()
# Called by: Modules/Flashscore/fs_league_enricher.py (enrichment vertical slice)

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Type

from Core.Scrapers.fs_flashscore_scraper import FlashscoreSiteScraper
from Core.Scrapers.fb_football_scraper import FootballComFootballScraper
from Core.Scrapers.fb_basketball_adapter import FootballComBasketballScraper

RegistryKey = Tuple[str, str]

_REGISTRY: Dict[RegistryKey, Type[Any]] = {
    ("flashscore", "football"): FlashscoreSiteScraper,
    ("flashscore", "basketball"): FlashscoreSiteScraper,
    ("football.com", "football"): FootballComFootballScraper,
    ("football.com", "basketball"): FootballComBasketballScraper,
}


def _norm_site(site: str) -> str:
    s = (site or "").strip().lower().replace(" ", "")
    if s in ("fb", "footballcom", "www.football.com"):
        return "football.com"
    if s in ("fs", "www.flashscore.com"):
        return "flashscore"
    return site.strip().lower()


def get_scraper(site: str, sport: str = "football") -> Any:
    """Instantiate the scraper for ``site`` + ``sport`` (defaults: flashscore / football)."""
    sp = (sport or "football").strip().lower()
    st = _norm_site(site)
    if st == "flashscore":
        return FlashscoreSiteScraper(sport=sp)
    if st == "football.com":
        cls = _REGISTRY.get(("football.com", sp))
        if cls is None:
            raise KeyError(f"No scraper registered for site={site!r} sport={sport!r}")
        return cls()
    raise KeyError(f"Unknown scraper site {site!r} (expected flashscore or football.com)")


def list_registered_scraper_keys() -> List[RegistryKey]:
    """Return registered (site, sport) pairs (for docs / diagnostics)."""
    return sorted(_REGISTRY.keys())
