# Deploying ConcertNOW live

## Database history: MySQL free-tier hosting turned out to be too unreliable

Two free MySQL hosts were tried, in order, and both failed within about a
week for reasons that had nothing to do with the app itself:

1. **db4free.net** — the domain lapsed and was re-registered by an unrelated
   party; it started serving unrelated content and was dropped immediately,
   before any real credentials were used there.
2. **freesqldatabase.com** — verified more carefully this time (WHOIS
   history, Wayback Machine snapshots) before switching to it, and it worked
   correctly for about a week — until the account expired outright ("free
   accounts expire" is the service's actual policy, confirmed by their own
   email). At that point the live app started returning `503 Database
   connection failed` on login.

Rather than chase a third free MySQL host with the same expiry risk, the
live deployment now runs on **SQLite** — a single file, bundled with the
app, created and seeded automatically the first time it runs
(`init_db()` in `deploy/app.py`). No signup, no host, no credentials, no
expiry. The trade-off (and why this wasn't the first choice) is explained
below.

**The full MySQL version — schema, both triggers, both stored procedures —
is unchanged and still the "real" version of this project**: `setup.sql`,
`code/schema.sql`, `code/advanced_database_programs.sql`. Verified working
against a real local MySQL instance. `deploy/` is a separately adapted copy
for the constraints of free public hosting; `code/` stays the authentic,
unmodified reference.

## 1. Push this repo to GitHub

✅ Done — pushed to [github.com/wen11235/data-portfolio](https://github.com/wen11235/data-portfolio), GitHub Pages live at [wen11235.github.io/data-portfolio](https://wen11235.github.io/data-portfolio/).

## 2. Hosting — Render.com

✅ The Render web service already exists (`concertnow`, connected to this
repo, root directory `projects/09-concert-trip-planner/deploy`). Since the
database is now a bundled SQLite file instead of an external host, **no
environment variables are needed at all** — if the old `DB_HOST` /
`DB_PORT` / `DB_DATABASE` / `DB_USER` / `DB_PASSWORD` variables are still
set on the service from the MySQL days, they're simply unused now and can
be deleted from Render's dashboard (Environment tab) whenever convenient —
not required for the app to work, just tidy-up.

Pushing to `main` triggers an automatic redeploy. To verify manually:
```bash
curl -s -X POST https://concertnow-xxxx.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"5551234567","password":"demo1234"}'
```
should return `{"message":"Login successful.", ...}` — not a 503.

## Known limitations, worth knowing about (both deliberate, not bugs)

- **No stored procedures or triggers at the database layer.** SQLite
  supports neither. Both are reimplemented as plain Python functions in
  `deploy/app.py` — `compute_enforced_visibility()` for the visibility
  trigger logic, `copy_public_trip_to_user()` for the
  `sp_copy_public_trip_to_user` transaction (same validate → duplicate-check
  → insert sequence, same commit/rollback semantics, just Python instead of
  a `CALL`). Locking is coarser too — SQLite takes a whole-database write
  lock during a transaction rather than a per-row lock. None of this changes
  the real, unmodified MySQL version's SQL (see `setup.sql` and
  `code/advanced_database_programs.sql`) — the trigger/procedure code there
  is untouched and still the thing to point to when discussing this project.
- **Data doesn't persist across restarts.** Render's free tier has no
  persistent disk — the SQLite file lives on ephemeral storage and resets to
  the seed data whenever the service restarts (which happens on every
  redeploy, and after 15 minutes of inactivity spins the service down
  entirely). Anything a visitor adds — a new registration, a new trip — is
  gone once the service cycles. For a portfolio demo this is arguably a
  feature (always a clean, working demo state for the next visitor) rather
  than a bug, but it's not how a real production app would behave, and
  worth being upfront about if asked.
- **Render free tier spins down after 15 minutes of inactivity.** The first
  request after that takes ~30-60 seconds to cold-start. If a recruiter
  clicks the link and it looks slow/broken at first, that's why.

## Status

✅ Live and verified: **https://data-portfolio-egrt.onrender.com** — wired
into the homepage card, README.md, and report.html as "Live Demo" links.
