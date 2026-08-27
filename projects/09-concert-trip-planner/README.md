# ConcertNOW: Concert & Trip Planning App

**TL;DR:** A full-stack Flask + MySQL app that combines concert search, hotel matching, and shareable itineraries into one workflow — built as a 3-person team project for a graduate database systems course (CS411, UIUC). My role: backend logic, API development, and integrating triggers and transaction-based stored procedures into the Flask app.

[📄 Full report](report.html) · [💻 Code](code/) · [📑 Project Report PDF](Project_Report.pdf) · [📑 Indexing Analysis PDF](Stage3_Indexing_Analysis.pdf)

<!-- TODO once deployed: · [🌐 Live Demo](https://your-app.onrender.com) -->

**Live demo**: not yet deployed — see [DEPLOY.md](DEPLOY.md) for the ready-to-go deployment guide (freesqldatabase.com + Render.com, both free, ~15 min).

## Team & my role

Built with **Yi-Hsin Chang** and **Zoe Hanson** as "Team DataDucks" for CS411 (Database Systems, UIUC). Division of labor, from our submitted project report: Yi-Hsin led backend database implementation — writing SQL queries, designing stored procedures, and managing the Cloud SQL connection. **I concentrated on backend logic, API development, and integrating advanced database features (triggers and transaction-based stored procedures) into the Flask application.** Zoe built the full frontend — page structure, styling, and keeping the interface consistent with the database's enforced rules.

## Demo note

The production app connects to a Google Cloud SQL instance through a local Cloud SQL Proxy tunnel — not reachable from outside our own machines. The screenshots below are from a **locally reconstructed instance**: the exact schema and SQL programs from `code/schema.sql` and `code/advanced_database_programs.sql`, running against a local MySQL server seeded with a small set of realistic sample data, with the real `app.py` pointed at it unmodified. Same code, same schema, same triggers and stored procedures — just a different (fake) dataset behind it, because the real one isn't reachable from here.

## Live deployment: two free MySQL hosts, two failures, then SQLite

Deploying a genuinely public version (see [DEPLOY.md](DEPLOY.md)) turned into its own small case study in free-tier infrastructure reliability. First attempt (db4free.net): the domain lapsed and was re-registered by an unrelated party before any credentials were used there. Second attempt (freesqldatabase.com), chosen after actually verifying its legitimacy first (WHOIS history, Wayback Machine snapshots): worked for about a week, then the account expired outright — a documented policy of that service, not a bug on this end. Along the way, that host's free tier also turned out not to grant the `TRIGGER` privilege (confirmed via `SHOW GRANTS FOR CURRENT_USER()`), so the visibility rule was already running as a `compute_enforced_visibility()` Python function instead of a database trigger before the account expired entirely.

Rather than chase a third free MySQL host with the same expiry risk, the live deployment now runs on **SQLite** — a single bundled file, created and seeded automatically on first run, no signup or credentials at all. The trade-off: SQLite has neither triggers nor stored procedures, so both the visibility rule *and* the `sp_copy_public_trip_to_user` transaction are reimplemented as plain Python (`deploy/app.py`) — same logic, same commit/rollback semantics, database layer traded for application layer purely for this hosting constraint. And since Render's free tier has no persistent disk, the database resets to seed data on every restart — a real limitation, documented rather than hidden (see [DEPLOY.md](DEPLOY.md) for the full breakdown).

**None of this touches the actual project.** `setup.sql` and `code/advanced_database_programs.sql` are unchanged — the real triggers and stored procedures, verified working against a real local MySQL instance. `deploy/` is a separately adapted copy for the realities of free public hosting; `code/` stays the authentic, unmodified reference.

## What it does

- **Search** concerts by city and date (sourced from a static Ticketmaster data pull, after the team dropped live API integration — see below)
- **Match hotels** to a selected concert by city (`HOTEL.City = VENUE.City`)
- **Build an itinerary**: pick a concert, optionally a hotel, add notes, set public/private visibility
- **Community page**: browse other users' public itineraries and copy them to your own trips
- **Trip stats dashboard**: total trips, public trips, distinct cities visited — computed in the database, not the app layer

## Schema

7 tables: `USER`, `VENUE`, `EVENT`, `HOTEL`, `REVIEW`, `TRIP`, `SAVE`. One deliberate design change worth calling out: the original schema stored hotel/venue location as latitude/longitude, which implied a functional dependency `(Latitude, Longitude) → (State, City)` and left the schema short of Third Normal Form. Revised to `Address` + `Zipcode` + `City` + `State` instead — removes the FD problem and is a more natural fit for the app's actual access pattern (displaying and city-matching hotels, not geospatial distance calculations).

## Advanced database programs

**Two triggers** enforce a data-quality rule at the database layer rather than trusting the frontend: a trip is automatically set to `Private` on insert or update if it's missing a hotel or has a note under 20 characters — keeping incomplete/draft trips out of the public Community page even if a bug or an external script bypasses frontend validation.

**Two stored procedures**:
- `sp_get_user_trip_stats` — aggregates a user's total trips, public trips, and distinct cities visited directly in the database, powering the trip-stats dashboard without the app layer computing it.
- `sp_copy_public_trip_to_user` — the "Save to My Trips" feature, wrapped in an explicit transaction (`READ COMMITTED` isolation, row-level locking via `FOR UPDATE`) with validation, duplicate-checking, and rollback on failure. Copying a trip is only ever fully applied or fully rolled back, even under concurrent copies of the same trip.

```sql
-- from code/advanced_database_programs.sql
SELECT ... FROM TRIP T JOIN EVENT E ON T.EventId = E.EventId
WHERE T.TripId = p_source_trip_id AND T.Visibility = 1
FOR UPDATE;

IF v_event_id IS NULL THEN
    SET p_status_code = 1; ROLLBACK;
ELSEIF EXISTS (SELECT 1 FROM TRIP WHERE UserId = p_target_user_id AND EventId = v_event_id) THEN
    SET p_status_code = 2; ROLLBACK;
ELSE
    INSERT INTO TRIP (...) VALUES (...);
    COMMIT;
END IF;
```

## Index design: an honest negative result

Query cost analysis (`EXPLAIN`) across 4 representative queries, testing several candidate indexes on each. Not every index helped:

| Query | Baseline cost | Best index tried | Cost after |
|---|---|---|---|
| Hotels in a city with avg rating ≥ 4.5 | 288,072 | `HOTEL(City)` | **203,339** ✅ |
| Top venues by upcoming events + hotel quality | 96,654 | `EVENT(EventDate)` | 96,654 (no change) |
| Hotels in NYC, most reviews, above-avg rating | 311,108 | `HOTEL(City, HotelCode)` composite | **205,124** ✅ |
| Upcoming events in the most popular zipcode | 7,122 | `EVENT(EventDate)` | 17,046 (**worse**) |

The `REVIEW(Rating)` index actually *increased* cost for query 3 before the composite `HOTEL(City, HotelCode)` index found the real win — and one index made a query slower, not faster. Worth keeping in the writeup rather than only reporting the indexes that worked: location-based and join-supporting indexes consistently helped; indexes on columns used only for aggregation/sorting mostly didn't, because the query's real cost was in building temporary tables for the joins, not scanning the base table. Full detail in the [indexing analysis PDF](Stage3_Indexing_Analysis.pdf).

## Skills demonstrated

Flask REST API design, MySQL triggers and stored procedures, transaction isolation and row locking, schema normalization (3NF), query cost analysis and index design, working on a 3-person engineering team with a clean division of labor between backend, database, and frontend.
