# market_ontology.py: Single source of truth for all 30 market-outcome options.
# Part of LeoBook Core — Intelligence
#
# Classes: MarketDefinition, MarketOntology
# Strategy: Pydantic-validated ontology loaded from ranked_markets JSON.
# v1.0-2026-03-19: Initial release — 30-dim action space.

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Tuple
import json
from pathlib import Path


class MarketDefinition(BaseModel):
    rank: int
    market_outcome: str
    likelihood_percent: float
    base_market: str
    market_id: str
    category: str
    exact_outcome: str
    line: Optional[str]
    marketGuide: str
    semantic_meaning: str = Field(..., description="Clear statistical interpretation e.g. 'Total goals > 3.5'")
    typical_xg_range: Tuple[float, float] = Field(..., description="Expected total xG range where this market is optimal")
    risk_profile: str = Field(..., description="safe | balanced | aggressive")
    statistical_edge_conditions: List[str] = Field(default_factory=list)


class MarketOntology(BaseModel):
    markets: Dict[str, MarketDefinition] = Field(..., description="key = market_outcome string")
    version: str = "v1.0-2026-03-19"
    total_markets: int = 30

    @classmethod
    def load(cls) -> "MarketOntology":
        path = Path(__file__).resolve().parent.parent.parent / "Data" / "Store" / "ranked_markets_likelihood_updated_with_team_ou.json"
        data = json.loads(path.read_text())
        ontology = {}
        for entry in data["ranked_market_outcomes"][:30]:  # ONLY first 30
            # Strip keys the Pydantic model doesn't expect
            entry = {k: v for k, v in entry.items() if k not in ("lines_available", "variants", "selectors")}

            line = entry.get("line")
            outcome = entry["exact_outcome"]
            base = entry["base_market"]
            likelihood = entry["likelihood_percent"]

            # --- Auto-generate semantic_meaning, typical_xg_range, risk_profile ---

            # Over/Under (total goals)
            if base == "Over/Under":
                semantic = f"Total goals {'over' if outcome == 'Over' else 'under'} {line}"
                if outcome == "Over":
                    xg_low = float(line) - 0.5 if line else 1.5
                    xg_high = float(line) + 1.5 if line else 4.5
                    risk = "safe" if likelihood >= 70 else ("balanced" if likelihood >= 45 else "aggressive")
                else:
                    xg_low = 0.0
                    xg_high = float(line) - 0.3 if line else 2.2
                    risk = "safe" if likelihood >= 60 else "balanced"
                edges = [f"Avg total goals {'>' if outcome == 'Over' else '<'} {line} in last 10"]

            # Home/Away Team Goals O/U
            elif base in ("Home Team Goals O/U", "Away Team Goals O/U"):
                side = "home" if "Home" in base else "away"
                semantic = f"{side.title()} team goals over {line}"
                xg_low = float(line) - 0.3 if line else 0.5
                xg_high = float(line) + 1.2 if line else 2.5
                risk = "safe" if likelihood >= 60 else ("balanced" if likelihood >= 35 else "aggressive")
                edges = [f"Team xG ({side}) > {line} in last 5"]

            # Double Chance
            elif base == "Double Chance":
                if outcome == "1X":
                    semantic = "Home win or Draw (1X)"
                elif outcome == "12":
                    semantic = "Home win or Away win — no draw (12)"
                elif outcome == "X2":
                    semantic = "Draw or Away win (X2)"
                else:
                    semantic = entry["marketGuide"]
                xg_low, xg_high = 0.0, 5.0
                risk = "safe"
                edges = ["Home advantage > 55%" if "1" in outcome else "Low draw probability"]

            # GG/NG (Both Teams to Score)
            elif base == "GG/NG":
                if outcome == "GG":
                    semantic = "Both teams score at least one goal"
                    xg_low, xg_high = 1.0, 4.5
                    risk = "balanced"
                    edges = ["Both teams xG > 0.8"]
                else:
                    semantic = "At least one team fails to score"
                    xg_low, xg_high = 0.0, 3.0
                    risk = "balanced"
                    edges = ["One team xG < 0.5"]

            # 1st Half Over/Under
            elif base == "1st Half O/U":
                semantic = f"1st half goals over {line}"
                xg_low = 0.3
                xg_high = float(line) + 1.0 if line else 2.0
                risk = "balanced"
                edges = [f"1H avg goals > {line} in last 10"]

            # 1X2 (match result)
            elif base == "1X2":
                labels = {"1": "Home win", "X": "Draw", "2": "Away win"}
                semantic = labels.get(outcome, entry["marketGuide"])
                xg_low, xg_high = 0.0, 5.0
                risk = "balanced"
                edges = [f"{'Home' if outcome == '1' else 'Away'} win probability > 50%"]

            # Draw No Bet
            elif base == "Draw No Bet":
                side = "Home" if outcome == "1" else "Away"
                semantic = f"{side} win or refund on draw"
                xg_low, xg_high = 0.0, 5.0
                risk = "safe"
                edges = [f"{side} expected to win but draw possible"]

            # Corners O/U
            elif base == "Corners O/U":
                semantic = f"Total corners over {line}"
                xg_low, xg_high = 0.0, 5.0  # xG not directly relevant
                risk = "balanced"
                edges = [f"Avg corners > {line} in last 10"]

            # Asian Handicap
            elif base == "Asian Handicap":
                semantic = f"Home team with {line} handicap applied"
                xg_low, xg_high = 0.0, 5.0
                risk = "balanced"
                edges = ["Home xG advantage > 0.5"]

            # Cards O/U
            elif base == "Cards O/U":
                semantic = f"Total cards over {line}"
                xg_low, xg_high = 0.0, 5.0
                risk = "balanced"
                edges = [f"Avg cards > {line} in last 10 matches"]

            # 1st Half 1X2
            elif base == "1st Half 1X2":
                labels_ht = {"1": "Home leading at HT", "X": "Draw at half-time", "2": "Away leading at HT"}
                semantic = labels_ht.get(outcome, entry["marketGuide"])
                xg_low, xg_high = 0.0, 2.5
                risk = "balanced"
                edges = ["HT draw rate > 40% historically"]

            # Clean Sheet
            elif "Clean Sheet" in base:
                side = "Home" if "Home" in base else "Away"
                semantic = f"{side} team keeps a clean sheet"
                xg_low, xg_high = 0.0, 2.5
                risk = "balanced"
                edges = [f"{side} concedes < 0.8 xG per match"]

            # Any Team 2UP
            elif base == "Any Team 2UP":
                semantic = "Any team takes a two-goal lead at any point"
                xg_low, xg_high = 1.5, 5.0
                risk = "balanced"
                edges = ["xG difference > 1.0 expected"]

            # DC & GG/NG combo
            elif base == "DC & GG/NG":
                semantic = f"Double Chance {outcome.split(' & ')[0]} and Both Teams Score"
                xg_low, xg_high = 1.0, 5.0
                risk = "balanced"
                edges = ["Home advantage + both teams offensive"]

            # Score In Both Halves
            elif base == "Score In Both Halves":
                semantic = f"Home team scores in both halves"
                xg_low, xg_high = 1.5, 4.0
                risk = "aggressive"
                edges = ["Home xG > 0.6 in each half"]

            # Over/Under 3.5 (already caught above but keeping for clarity)

            # To Score First & Win
            elif base == "To Score First & Win":
                semantic = f"Home team scores first and wins"
                xg_low, xg_high = 1.5, 4.5
                risk = "aggressive"
                edges = ["Home scores first in > 55% of matches"]

            # Penalty In Match
            elif base == "Penalty In Match":
                semantic = "A penalty is awarded during the match"
                xg_low, xg_high = 0.0, 5.0
                risk = "aggressive"
                edges = ["Referee avg penalties > 0.3/match"]

            # HT/FT
            elif base == "HT/FT":
                semantic = f"Home leads at HT and wins FT ({outcome})"
                xg_low, xg_high = 1.5, 4.5
                risk = "aggressive"
                edges = ["Home HT win rate > 35%"]

            # Win to Nil
            elif "Win to Nil" in base:
                side = "Home" if "Home" in base else "Away"
                semantic = f"{side} team wins without conceding"
                xg_low, xg_high = 1.0, 3.5
                risk = "aggressive"
                edges = [f"{side} xG > 1.5 and opponent xG < 0.6"]

            # Fallback
            else:
                semantic = entry["marketGuide"]
                xg_low, xg_high = 0.0, 5.0
                risk = "balanced"
                edges = []

            entry["semantic_meaning"] = semantic
            entry["typical_xg_range"] = (xg_low, xg_high)
            entry["risk_profile"] = risk
            entry["statistical_edge_conditions"] = edges
            ontology[entry["market_outcome"]] = MarketDefinition(**entry)
        return cls(markets=ontology)


if __name__ == "__main__":
    ont = MarketOntology.load()
    print(f"[OK] Ontology loaded with {len(ont.markets)} markets")
    print(ont.markets["Over/Under - Under 3.5"].model_dump_json(indent=2) if "Over/Under - Under 3.5" in ont.markets else "")
    # Print the rank-16 entry as test (Under 2.5)
    key = "Over/Under - Under (2.5 line)"
    if key in ont.markets:
        print(f"\n--- Test: {key} ---")
        print(ont.markets[key].model_dump_json(indent=2))
    # Summary table
    print(f"\n{'Rank':<6}{'Market Outcome':<50}{'Likelihood':<12}{'Risk':<12}")
    print("-" * 80)
    for m in sorted(ont.markets.values(), key=lambda x: x.rank):
        print(f"{m.rank:<6}{m.market_outcome:<50}{m.likelihood_percent:<12}{m.risk_profile:<12}")
