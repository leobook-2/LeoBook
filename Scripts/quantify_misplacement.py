"""Quantify prediction team misplacement scale from live DB."""
import sqlite3, re, os

DB = 'Data/Store/leobook.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ── 1 ▸ Parse team name from match_link URL slug ─────────────────────────────
def slug_to_name_approx(slug: str) -> str:
    """football/home-slug-ID/away-slug-ID → rough name from slug."""
    return slug.replace('-', ' ').title().strip()

def parse_match_link(link: str):
    """Extract (home_slug, home_id, away_slug, away_id) from Flashscore match_link."""
    if not link:
        return None
    m = re.search(r'/match/football/([^/]+)/([^/]+)/', link)
    if not m:
        return None
    h, a = m.group(1), m.group(2)
    h_id = h.rsplit('-', 1)[-1] if '-' in h else ''
    a_id = a.rsplit('-', 1)[-1] if '-' in a else ''
    h_slug = h.rsplit('-', 1)[0] if '-' in h else h
    a_slug = a.rsplit('-', 1)[0] if '-' in a else a
    return h_id, a_id, h_slug, a_slug

# ── 2 ▸ Check schedules: home_team_id vs match_link home ID ──────────────────
print("\n=== SCHEDULES: team_id vs match_link mismatch ===")
rows = conn.execute(
    "SELECT fixture_id, home_team_id, away_team_id, home_team_name, away_team_name, match_link "
    "FROM schedules WHERE match_link IS NOT NULL AND match_link != '' LIMIT 5000"
).fetchall()

id_mismatch = 0
name_swapped = 0
total_checked = 0

swap_examples = []

for r in rows:
    parsed = parse_match_link(r['match_link'])
    if not parsed:
        continue
    url_h_id, url_a_id, url_h_slug, url_a_slug = parsed
    db_h_id = r['home_team_id'] or ''
    db_a_id = r['away_team_id'] or ''
    total_checked += 1

    if url_h_id and db_h_id and url_h_id != db_h_id:
        id_mismatch += 1
        # Check if they're swapped
        if url_h_id == db_a_id and url_a_id == db_h_id:
            name_swapped += 1
            if len(swap_examples) < 5:
                swap_examples.append({
                    'fixture_id': r['fixture_id'],
                    'db_home': r['home_team_name'],
                    'db_away': r['away_team_name'],
                    'db_home_id': db_h_id,
                    'db_away_id': db_a_id,
                    'url_home_slug': url_h_slug,
                    'url_away_slug': url_a_slug,
                    'url_home_id': url_h_id,
                    'url_away_id': url_a_id,
                    'match_link': r['match_link'][:80]
                })

print(f"Checked: {total_checked}")
print(f"ID mismatches: {id_mismatch} ({100*id_mismatch/max(total_checked,1):.1f}%)")
print(f"  of which SWAPPED (home<->away): {name_swapped}")

print("\n--- Swap examples ---")
for ex in swap_examples:
    print(f"  {ex['fixture_id']}: DB home='{ex['db_home']}' ({ex['db_home_id']}) | URL home slug='{ex['url_home_slug']}' ({ex['url_home_id']})")
    print(f"           DB away='{ex['db_away']}' ({ex['db_away_id']}) | URL away slug='{ex['url_away_slug']}' ({ex['url_away_id']})")
    print(f"    link: {ex['match_link']}")

# ── 3 ▸ Check predictions: home_team_id vs match_link ────────────────────────
print("\n=== PREDICTIONS: team_id vs match_link mismatch ===")
pred_rows = conn.execute(
    "SELECT fixture_id, home_team, away_team, home_team_id, away_team_id, match_link "
    "FROM predictions WHERE match_link IS NOT NULL AND match_link != '' LIMIT 2000"
).fetchall()

p_total = p_mismatch = p_swapped = 0
pred_swap_examples = []

for r in pred_rows:
    parsed = parse_match_link(r['match_link'])
    if not parsed:
        continue
    url_h_id, url_a_id, _, _ = parsed
    db_h_id = r['home_team_id'] or ''
    db_a_id = r['away_team_id'] or ''
    p_total += 1
    if url_h_id and db_h_id and url_h_id != db_h_id:
        p_mismatch += 1
        if url_h_id == db_a_id and url_a_id == db_h_id:
            p_swapped += 1
            if len(pred_swap_examples) < 5:
                pred_swap_examples.append(dict(r))

print(f"Checked: {p_total}")
print(f"ID mismatches: {p_mismatch} ({100*p_mismatch/max(p_total,1):.1f}%)")
print(f"  of which SWAPPED: {p_swapped} ({100*p_swapped/max(p_total,1):.1f}%)")

print("\n--- Prediction swap examples ---")
for ex in pred_swap_examples[:3]:
    ml = ex.get('match_link', '')
    p = parse_match_link(ml)
    url_info = f"URL: {ml[:80]}" if ml else ""
    print(f"  {ex['fixture_id']}: DB home='{ex['home_team']}' ({ex['home_team_id']}) | {url_info}")

conn.close()
