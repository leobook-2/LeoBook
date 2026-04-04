# Scrapers package: shared site + sport scraping interfaces for LeoBook.
# Part of LeoBook Core — Scrapers

from Core.Scrapers.site_sport_scraper import SiteSportScraper
from Core.Scrapers.fs_flashscore_scraper import FlashscoreSiteScraper
from Core.Scrapers.fb_football_scraper import FootballComFootballScraper
from Core.Scrapers.fb_basketball_adapter import FootballComBasketballScraper
from Core.Scrapers.registry import get_scraper, list_registered_scraper_keys

__all__ = [
    "SiteSportScraper",
    "FlashscoreSiteScraper",
    "FootballComFootballScraper",
    "FootballComBasketballScraper",
    "get_scraper",
    "list_registered_scraper_keys",
]
