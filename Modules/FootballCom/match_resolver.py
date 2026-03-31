# match_resolver.py: Deterministic match resolution for Football.com pairing.
# Part of LeoBook Modules — FootballCom
#
# v2.0 (2026-03-31): DELETED all fuzzy matching, confidence scores, and Supabase lookups.
#       Resolution is now 100% deterministic (League + Date + Normalized Team Names).
#       Built for "Instant Resolution" inside the league extraction worker.

import logging
import re
import sqlite3
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class FixtureResolver:
    """
    Deterministic, in-memory fixture resolver.
    Matches extracted Football.com matches against known Flashscore fixtures
    based on exact league_id + exact date (WAT) + normalized team names.
    """

    def __init__(self):
        pass

    @staticmethod
    def _normalize(name: str) -> str:
        """Standardized normalization for deterministic team name comparison."""
        name = name.strip().lower()
        name = re.sub(r'[^a-z0-9 ]', '', name)  # strip accents/punctuation
        name = re.sub(r'\s+', ' ', name).strip()
        return name

    async def resolve_deterministic(
        self,
        fs_fix: Dict,
        fb_candidates: List[Dict],
    ) -> Tuple[Optional[Dict], float, str]:
        """
        In-memory deterministic resolution.
        
        Args:
            fs_fix: The Flashscore fixture from the 'schedules' table.
            fb_candidates: List of matches extracted from the Football.com league page.
            
        Returns: (best_match_dict, score, method_str)
        """
        if not fb_candidates:
            return None, 0.0, 'no_candidates'

        # 1. Flashscore Target (Normalized)
        target_home = self._normalize(fs_fix.get('home_team_name') or fs_fix.get('home_team') or '')
        target_away = self._normalize(fs_fix.get('away_team_name') or fs_fix.get('away_team') or '')
        target_date = fs_fix.get('date', '')

        if not target_home or not target_away or not target_date:
            return None, 0.0, 'bad_fs_data'

        # 2. Iterate through candidates for an IDENTICAL match
        for fb_match in fb_candidates:
            fb_date = fb_match.get('date', '')
            
            # STRICT DATE CHECK (Both now use WAT)
            if fb_date != target_date:
                continue

            fb_home = self._normalize(fb_match.get('home', fb_match.get('home_team', '')))
            fb_away = self._normalize(fb_match.get('away', fb_match.get('away_team', '')))

            if fb_home == target_home and fb_away == target_away:
                # 100% Deterministic Match Found
                enriched = dict(fb_match)
                enriched['fixture_id'] = fs_fix['fixture_id']
                enriched['matched'] = True
                return enriched, 1.0, 'deterministic_v2.0'

        return None, 0.0, 'unresolved'

    async def resolve(
        self,
        fs_fix: Dict,
        fb_matches: List[Dict],
        conn: sqlite3.Connection = None,
    ) -> Tuple[Optional[Dict], float, str]:
        """Backward-compatible entry point for the new deterministic resolver."""
        return await self.resolve_deterministic(fs_fix, fb_matches)