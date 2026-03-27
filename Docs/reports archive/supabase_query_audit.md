# LeoBook Flutter — Supabase Query Audit

Complete trace of every Supabase query, linked from **Repository → Cubit → Screen**.

---

## 1. Today's Matches & Filters (Live / Finished / Scheduled)

### Data Fetch — [data_repository.dart:L79-140](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L79-L140)

```dart
// fetchMatches({DateTime? date})
var query = _supabase.from('schedules').select();
if (date != null) {
  query = query.eq('date', dateStr);  // e.g. '2026-03-27'
}
final ordered = query.order('date', ascending: false);
final response = date != null ? await ordered : await ordered.limit(300);
```

**SQL Equivalent:**
```sql
SELECT * FROM schedules
WHERE date = '2026-03-27'
ORDER BY date DESC;
```

### Prediction Enrichment — [data_repository.dart:L24-63](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L24-L63)

```dart
// _fetchPredictionMap({dateStr})
predRows = await _supabase
    .from('predictions').select().eq('date', dateStr);
```

**SQL Equivalent:**
```sql
SELECT * FROM predictions WHERE date = '2026-03-27';
```

### Recommendations — [data_repository.dart:L205-245](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L205-L245)

```dart
await _supabase.from('predictions').select()
    .gt('recommendation_score', 0)
    .order('recommendation_score', ascending: false)
    .limit(100);
```

### Orchestration — [home_cubit.dart:L89-116](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/logic/cubit/home_cubit.dart#L89-L116)

Calls [fetchMatches(date: now)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#79-141) → merges with predictions → applies client-side filters.

### Client-Side Filters — [home_cubit.dart:L651-694](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/logic/cubit/home_cubit.dart#L651-L694)

| Filter | Code | Logic |
|--------|------|-------|
| **Live** | `match.isLive` | `status contains 'live', 'halftime', etc.` |
| **Finished** | `match.isFinished` | `status contains 'finish', 'ft', 'aet', etc.` |
| **Scheduled** | `displayStatus == ""` | `status contains 'sched' or empty` |
| **Sport** | `m.sport == sport` | Client-side equality |
| **League** | `leagues.contains(m.league)` | Client-side membership |
| **Odds range** | `mOdds >= minO && mOdds <= maxO` | Client-side range |
| **Confidence** | `confs.contains(m.confidence)` | Client-side membership |

### Realtime Subscriptions — [data_repository.dart:L358-391](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L358-L391)

```dart
_supabase.from('live_scores').stream(primaryKey: ['fixture_id']);
_supabase.from('predictions').stream(primaryKey: ['fixture_id']);
_supabase.from('schedules').stream(primaryKey: ['fixture_id']);
_supabase.from('teams').stream(primaryKey: ['name']);
```

---

## 2. Match Detail (Form, H2H, Standings)

### Screen Entry — [match_details_screen.dart:L48-90](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/match_details_screen.dart#L48-L90)

### Home Team Last 10 — [data_repository.dart:L142-185](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L142-L185)

```dart
// getTeamMatches(teamName)
await _supabase.from('schedules').select()
    .or('home_team.eq."$teamName",away_team.eq."$teamName"')
    .order('date', ascending: false).limit(20);
// Fuzzy fallback if empty:
.or('home_team.ilike."%$teamName%",away_team.ilike."%$teamName%"')
```

**SQL Equivalent:**
```sql
SELECT * FROM schedules
WHERE home_team = 'Arsenal' OR away_team = 'Arsenal'
ORDER BY date DESC LIMIT 20;
```

Then client-side: `.where(isPast).take(10)` — [match_details_screen.dart:L77](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/match_details_screen.dart#L77)

### Away Team Last 10 — Same query with `match.awayTeam`

### H2H — [data_repository.dart:L188-203](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L188-L203)

```dart
// getH2HMatches(teamA, teamB)
await _supabase.from('schedules').select()
    .or('and(home_team.eq."$teamA",away_team.eq."$teamB"),'
        'and(home_team.eq."$teamB",away_team.eq."$teamA")')
    .order('date', ascending: false).limit(10);
```

**SQL Equivalent:**
```sql
SELECT * FROM schedules
WHERE (home_team = 'Arsenal' AND away_team = 'Chelsea')
   OR (home_team = 'Chelsea' AND away_team = 'Arsenal')
ORDER BY date DESC LIMIT 10;
```

### League Table (Standings) — [data_repository.dart:L247-314](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L247-L314)

```dart
// fetchStandings({leagueId, season})
var query = _supabase.from('computed_standings').select()
    .eq('league_id', leagueId);
if (season != null) query = query.eq('season', season);
await query.order('points', ascending: false)
           .order('goal_difference', ascending: false);

// Enrich with team crests:
await _supabase.from('teams').select('name, crest')
    .inFilter('name', teamNames);
```

**SQL Equivalent:**
```sql
SELECT * FROM computed_standings
WHERE league_id = '1_100_KEUqwJAr'
ORDER BY points DESC, goal_difference DESC;

SELECT name, crest FROM teams WHERE name IN ('Arsenal', 'Chelsea', ...);
```

Called from — [match_details_screen.dart:L56-60](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/match_details_screen.dart#L56-L60)

---

## 3. League View (Table, Fixtures, Results, Archive)

### League Metadata — [data_repository.dart:L490-511](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L490-L511)

```dart
// fetchLeagueById(leagueId)
await _supabase.from('leagues').select()
    .eq('league_id', leagueId).maybeSingle();
```

Called from — [league_screen.dart:L52-57](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/league_screen.dart#L52-L57)

### League Table (Overview Tab) — [overview_tab.dart:L38-65](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/widgets/shared/league_tabs/overview_tab.dart#L38-L65)

Calls `repo.fetchStandings(leagueId, season)` + `repo.fetchMatches(date: now)` for featured predictions.

### Fixtures Tab — [fixtures_tab.dart:L41-60](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/widgets/shared/league_tabs/fixtures_tab.dart#L41-L60)

```dart
// Uses fetchFixturesByLeague(leagueId, season)
final allMatches = await repo.fetchFixturesByLeague(widget.leagueId, season: widget.season);
return allMatches.where((m) => !m.isFinished).toList(); // Upcoming only
```

### fetchFixturesByLeague — [data_repository.dart:L513-538](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L513-L538)

```dart
var query = _supabase.from('schedules').select()
    .eq('league_id', leagueId);
if (season != null) query = query.eq('season', season);
await query.order('date', ascending: false).limit(500);
// + prediction enrichment via _fetchPredictionMap
```

**SQL Equivalent:**
```sql
SELECT * FROM schedules
WHERE league_id = '1_100_KEUqwJAr' AND season = '2025/2026'
ORDER BY date DESC LIMIT 500;
```

### Results Tab — [results_tab.dart:L41-60](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/widgets/shared/league_tabs/results_tab.dart#L41-L60)

Same [fetchFixturesByLeague](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#513-539) query, then:
```dart
return allMatches.where((m) => m.isFinished).toList(); // Finished only
```

### Archive (Seasons) — [archive_tab.dart:L33](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/widgets/shared/league_tabs/archive_tab.dart#L33)

Calls [fetchLeagueSeasons(leagueId)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#539-560) → [data_repository.dart:L539-559](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L539-L559)

```dart
await _supabase.from('schedules').select('season')
    .eq('league_id', leagueId)
    .not('season', 'is', null)
    .order('season', ascending: false);
// Client-side: deduplicate into Set<String>
```

**SQL Equivalent:**
```sql
SELECT DISTINCT season FROM schedules
WHERE league_id = '1_100_KEUqwJAr' AND season IS NOT NULL
ORDER BY season DESC;
```

---

## 4. Team View (All-Time Matches Grouped)

### Screen Entry — [team_screen.dart:L53-139](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/team_screen.dart#L53-L139)

Calls:
1. `repo.getTeamMatches(teamName)` — same query as #2 above (last 20 matches)
2. `repo.getTeamStanding(teamName)` → [data_repository.dart:L338-354](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L338-L354)
3. `repo.fetchTeamCrests()` → [data_repository.dart:L316-330](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L316-L330)

### getTeamStanding — [data_repository.dart:L338-354](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#L338-L354)

```dart
await _supabase.from('computed_standings').select()
    .eq('team_name', teamName).maybeSingle();
```

### Grouping Logic — [team_screen.dart:L667-687](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/presentation/screens/team_screen.dart#L667-L687)

Groups by `leagueStage` (round) with month fallback:
```dart
if (m.leagueStage != null) groupKey = m.leagueStage!;
else groupKey = 'MAR 2026'; // month fallback
grouped.putIfAbsent(groupKey, () => []).add(m);
```

> [!IMPORTANT]
> **Missing: League-Season grouping.** The user wants matches grouped by `league → season → round`, but the current code only groups by round/month within a flat list of 20 matches. This requires a dedicated query or extended [getTeamMatches](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#142-186) to fetch all-time data.

---

## Summary Table

| Feature | Supabase Table | Repository Method | Query Type |
|---------|---------------|-------------------|------------|
| Today's matches | `schedules` | [fetchMatches(date:)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#79-141) | `.eq('date', ...)` |
| Prediction enrichment | `predictions` | [_fetchPredictionMap](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#22-64) | `.eq('date', ...)` or `.inFilter('fixture_id', ...)` |
| Recommendations | `predictions` | [fetchRecommendations()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#205-246) | `.gt('recommendation_score', 0)` |
| Home/Away form | `schedules` | [getTeamMatches(name)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#142-186) | `.or('home_team.eq...')` LIMIT 20 |
| H2H | `schedules` | [getH2HMatches(a, b)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#187-204) | `.or('and(...),...')` LIMIT 10 |
| League standings | `computed_standings` + `teams` | [fetchStandings(leagueId)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#247-315) | `.eq('league_id', ...)` |
| League fixtures | `schedules` | [fetchFixturesByLeague(id, season)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#513-539) | `.eq('league_id', ...).eq('season', ...)` |
| League results | `schedules` | same → client `.isFinished` filter | same query, client filter |
| Archive seasons | `schedules` | [fetchLeagueSeasons(id)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#539-560) | `.select('season').eq(...)` deduplicated |
| League metadata | [leagues](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/Modules/Flashscore/fs_league_extractor.py#436-452) | [fetchLeagueById(id)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#490-512) | `.eq('league_id', ...).maybeSingle()` |
| Team standing | `computed_standings` | [getTeamStanding(name)](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#338-355) | `.eq('team_name', ...).maybeSingle()` |
| Team crests | `teams` | [fetchTeamCrests()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#316-331) | `.select('name, crest')` |
| Live updates | `live_scores` | [watchLiveScores()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#358-362) | `.stream(primaryKey)` realtime |
| Schedule updates | `schedules` | [watchSchedules()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#378-392) | `.stream(primaryKey)` realtime |
| Prediction updates | `predictions` | [watchPredictions()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#363-377) | `.stream(primaryKey)` realtime |
| Crest updates | `teams` | [watchTeamCrestUpdates()](file:///c:/Users/Admin/Desktop/ProProjection/LeoBook/leobookapp/lib/data/repositories/data_repository.dart#432-443) | `.stream(primaryKey)` realtime |
