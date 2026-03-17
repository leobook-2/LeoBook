"""Deep-dive: check whether prediction team names match the actual schedule rows."""
import sqlite3, re

DB = 'Data/Store/leobook.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("\n=== INVESTIGATION: prediction team names vs schedules ===")

# Check the specific example row from before
fix_id = '0j4znHHk'
pred = conn.execute("SELECT * FROM predictions WHERE fixture_id=?", (fix_id,)).fetchone()
sched = conn.execute("SELECT * FROM schedules WHERE fixture_id=?", (fix_id,)).fetchone()
if pred and sched:
    print(f"\nfixture: {fix_id}")
    print(f"  prediction: home='{pred['home_team']}' ({pred['home_team_id']}) | away='{pred['away_team']}' ({pred['away_team_id']})")
    print(f"  schedules:  home_id={sched['home_team_id']} home_name='{sched['home_team_name']}' | away_id={sched['away_team_id']} away_name='{sched['away_team_name']}'")
    print(f"  match_link: {sched['match_link']}")
    # check teams table
    h_team = conn.execute("SELECT name FROM teams WHERE team_id=?", (sched['home_team_id'],)).fetchone()
    a_team = conn.execute("SELECT name FROM teams WHERE team_id=?", (sched['away_team_id'],)).fetchone()
    print(f"  teams table: home_team_id={sched['home_team_id']} -> name='{h_team['name'] if h_team else None}'")
    print(f"  teams table: away_team_id={sched['away_team_id']} -> name='{a_team['name'] if a_team else None}'")

# Check more: does predictions.home_team match schedules.home_team_name?
print("\n=== Bulk check: predictions.home_team vs schedules.home_team_name ===")
rows = conn.execute("""
    SELECT p.fixture_id, p.home_team AS p_home, p.away_team AS p_away,
           s.home_team_name AS s_home, s.away_team_name AS s_away,
           s.match_link
    FROM predictions p
    JOIN schedules s ON p.fixture_id = s.fixture_id
    WHERE s.match_link IS NOT NULL AND s.match_link != ''
    LIMIT 3000
""").fetchall()

total = len(rows)
name_mismatch_home = 0
name_mismatch_away = 0
swap_detected = 0
examples = []

for r in rows:
    h_match = (r['p_home'] or '').strip() == (r['s_home'] or '').strip()
    a_match = (r['p_away'] or '').strip() == (r['s_away'] or '').strip()
    if not h_match or not a_match:
        name_mismatch_home += (0 if h_match else 1)
        name_mismatch_away += (0 if a_match else 1)
        # Is it a swap?
        if (r['p_home'] or '').strip() == (r['s_away'] or '').strip() and \
           (r['p_away'] or '').strip() == (r['s_home'] or '').strip():
            swap_detected += 1
        if len(examples) < 8:
            examples.append(dict(r))

print(f"Total checked: {total}")
print(f"Home name mismatches: {name_mismatch_home} ({100*name_mismatch_home/max(total,1):.1f}%)")
print(f"Away name mismatches: {name_mismatch_away} ({100*name_mismatch_away/max(total,1):.1f}%)")
print(f"Confirmed SWAPS (home<->away transposed): {swap_detected}")

print("\n--- Mismatch examples ---")
for ex in examples:
    print(f"  {ex['fixture_id']}: p_home='{ex['p_home']}' vs s_home='{ex['s_home']}' | p_away='{ex['p_away']}' vs s_away='{ex['s_away']}'")

# Specifically check: do predictions use schedules.home_team_name or do they JOIN teams?
print("\n=== Check: how does prediction.home_team relate to teams.name? ===")
rows2 = conn.execute("""
    SELECT p.fixture_id, p.home_team AS p_home, p.home_team_id,
           t.name AS t_name,
           s.home_team_name AS s_home_name
    FROM predictions p
    LEFT JOIN teams t ON p.home_team_id = t.team_id
    LEFT JOIN schedules s ON p.fixture_id = s.fixture_id
    WHERE p.home_team_id IS NOT NULL AND p.home_team_id != ''
    LIMIT 500
""").fetchall()

t_name_match = sum(1 for r in rows2 if (r['p_home'] or '') == (r['t_name'] or ''))
s_name_match = sum(1 for r in rows2 if (r['p_home'] or '') == (r['s_home_name'] or ''))
print(f"Checked {len(rows2)} predictions:")
print(f"  p.home_team == teams.name: {t_name_match}/{len(rows2)} ({100*t_name_match/max(len(rows2),1):.1f}%)")
print(f"  p.home_team == sched.home_team_name: {s_name_match}/{len(rows2)} ({100*s_name_match/max(len(rows2),1):.1f}%)")

conn.close()
