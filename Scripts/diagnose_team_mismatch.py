"""Temporary diagnosis script for team misplacement audit."""
import sqlite3, os

# Find the correct DB
for path in ['Data/Store/leobook.db', 'Data/leobook.db']:
    if os.path.exists(path):
        print(f"\n=== DB: {path} ===")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"Tables: {tables}")
        
        if 'predictions' in tables:
            pred_cols = [c[1] for c in conn.execute("PRAGMA table_info(predictions)").fetchall()]
            print(f"\npredictions cols: {pred_cols}")
            sched_cols = [c[1] for c in conn.execute("PRAGMA table_info(schedules)").fetchall()]
            print(f"schedules cols: {sched_cols}")
            teams_cols = [c[1] for c in conn.execute("PRAGMA table_info(teams)").fetchall()]
            print(f"teams cols: {teams_cols}")
            
            # Sample predictions
            print("\n--- Sample predictions (last 5) ---")
            rows = conn.execute(
                "SELECT fixture_id, home_team, away_team, home_team_id, away_team_id, match_link, date FROM predictions ORDER BY rowid DESC LIMIT 5"
            ).fetchall()
            for r in rows:
                print(dict(r))
            
            # Cross-check one: prediction vs schedule JOIN
            print("\n--- Cross-check: prediction vs JOIN ---")
            r1 = conn.execute(
                "SELECT fixture_id, home_team, away_team, home_team_id, away_team_id FROM predictions WHERE home_team_id IS NOT NULL LIMIT 1"
            ).fetchone()
            if r1:
                fix_id = r1['fixture_id']
                print(f"fixture_id: {fix_id}")
                print(f"  predictions.home_team={r1['home_team']}  away_team={r1['away_team']}")
                print(f"  predictions.home_team_id={r1['home_team_id']}  away_team_id={r1['away_team_id']}")
                
                sched = conn.execute("SELECT * FROM schedules WHERE fixture_id=?", (fix_id,)).fetchone()
                if sched:
                    sd = dict(sched)
                    print(f"  schedules.home_team_id={sd.get('home_team_id')}  away_team_id={sd.get('away_team_id')}")
                    print(f"  schedules.home_team_name={sd.get('home_team_name')}  away_team_name={sd.get('away_team_name')}")
                
                # What the pipeline JOIN returns
                joined = conn.execute(
                    "SELECT h.name AS home_team_name, a.name AS away_team_name, s.home_team_id, s.away_team_id "
                    "FROM schedules s LEFT JOIN teams h ON s.home_team_id=h.team_id LEFT JOIN teams a ON s.away_team_id=a.team_id "
                    "WHERE s.fixture_id=?", (fix_id,)
                ).fetchone()
                if joined:
                    jd = dict(joined)
                    print(f"  JOIN: home_team_name={jd['home_team_name']}  away_team_name={jd['away_team_name']}")
                    # Check alignment
                    if jd['home_team_name'] != r1['home_team']:
                        print(f"  *** MISMATCH: prediction.home_team != JOIN.home_team_name ***")
                    else:
                        print(f"  [OK] home_team matches")
                    if jd['away_team_name'] != r1['away_team']:
                        print(f"  *** MISMATCH: prediction.away_team != JOIN.away_team_name ***")
                    else:
                        print(f"  [OK] away_team matches")
            
            # Check schedules for column name: home_team_name vs home_team
            print("\n--- schedules column check ---")
            sample_sched = conn.execute("SELECT * FROM schedules ORDER BY rowid DESC LIMIT 2").fetchall()
            for s in sample_sched:
                print(dict(s))
            
            # Count fb_matches
            if 'fb_matches' in tables:
                fb_count = conn.execute("SELECT COUNT(*) FROM fb_matches").fetchone()[0]
                fb_sample = conn.execute("SELECT * FROM fb_matches ORDER BY rowid DESC LIMIT 2").fetchall()
                print(f"\n--- fb_matches ({fb_count} rows) ---")
                for f in fb_sample:
                    print(dict(f))

        conn.close()
