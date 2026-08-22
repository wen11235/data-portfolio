# Deploying ConcertNOW live

Everything technical is ready in `deploy/` — schema, seed data, production
config. What's left needs your own accounts (I can't sign up for services on
your behalf). Should take about 15 minutes total.

## 1. Database — freesqldatabase.com (free MySQL)

> **Note:** originally this guide pointed at db4free.net. That domain lapsed
> and was re-registered by an unrelated party sometime before mid-2026 — it
> now serves unrelated content and should not be used. Verified before
> switching: freesqldatabase.com's domain has been registered since 2009,
> and its content has been consistent across Wayback Machine snapshots from
> 2019 through 2026 (same service, not recently hijacked).

1. ✅ You've already registered at **https://www.freesqldatabase.com/**.
2. Log in and find your database's connection details on your account
   dashboard — it'll show something like:
   - **Host**: e.g. `sql#.freesqldatabase.com` (a specific numbered host — copy exactly what's shown, don't guess it)
   - **Port**: usually `3306`
   - **Database name**: auto-generated, e.g. `sql1234567`
   - **Username**: usually the same as the database name
   - **Password**: what you set at signup
3. Load the schema, stored procedures, and seed data — from your terminal,
   from this `deploy/` folder (replace the placeholders with your actual
   values from step 2):
   ```bash
   mysql -h YOUR_HOST -P 3306 -u YOUR_USERNAME -p YOUR_DATABASE_NAME < setup_free_tier.sql
   ```
   **Use `setup_free_tier.sql`, not `setup.sql`.** Confirmed (via
   `SHOW GRANTS FOR CURRENT_USER()`) that freesqldatabase.com accounts get
   `CREATE ROUTINE`/`ALTER ROUTINE` (stored procedures work fine) but not
   `TRIGGER` — a common restriction on shared free MySQL hosting.
   `setup_free_tier.sql` is the same schema/procedures/seed data with the
   trigger section left out; the equivalent rule is enforced in
   `deploy/app.py` instead (see `compute_enforced_visibility()`) — already
   done, no action needed from you here.
4. Verify it worked:
   ```bash
   mysql -h YOUR_HOST -P 3306 -u YOUR_USERNAME -p YOUR_DATABASE_NAME -e "SHOW TABLES; SELECT * FROM VENUE; SHOW PROCEDURE STATUS WHERE Db = 'YOUR_DATABASE_NAME';"
   ```
   You should see 7 tables, 4 seeded venues, and 2 stored procedures
   (`sp_get_user_trip_stats`, `sp_copy_public_trip_to_user`).

## 2. Push this repo to GitHub

✅ Done — this repo is pushed to [github.com/wen11235/data-portfolio](https://github.com/wen11235/data-portfolio) and GitHub Pages is live at [wen11235.github.io/data-portfolio](https://wen11235.github.io/data-portfolio/).

## 3. Hosting — Render.com (free web service)

1. Go to **https://render.com** and sign up (GitHub sign-in is fastest — it
   also handles repo access permissions in one step).
2. **New +** → **Web Service** → connect your portfolio GitHub repo.
3. Fill in:
   - **Root Directory**: `projects/09-concert-trip-planner/deploy`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
4. Under **Environment Variables**, add these 5 (values from step 1 — your
   actual freesqldatabase.com host, not a placeholder):
   | Key | Value |
   |---|---|
   | `DB_HOST` | your freesqldatabase.com host (e.g. `sql#.freesqldatabase.com`) |
   | `DB_PORT` | `3306` |
   | `DB_DATABASE` | your freesqldatabase.com database name |
   | `DB_USER` | your freesqldatabase.com username |
   | `DB_PASSWORD` | your freesqldatabase.com password |
5. **Create Web Service**. First deploy takes a few minutes — watch the
   build log for errors.
6. Once live, Render gives you a URL like
   `https://concertnow-xxxx.onrender.com`. Test it: try logging in with the
   seeded demo account (`5551234567` / `demo1234`), search concerts in
   "San Francisco" on `2026-08-02`, check the Community page.

## Known limitations, worth knowing about (both free-tier things, not bugs)

- **The visibility rule runs in the app layer here, not as a MySQL trigger**
  — freesqldatabase.com doesn't grant the TRIGGER privilege. Functionally
  identical result; see the note in step 3 above and the `Deploy` section
  of `report.html` for the full explanation. The real trigger code is
  unchanged in `code/advanced_database_programs.sql` and works against any
  host that does grant TRIGGER (verified locally).
- **Render free tier spins down after 15 minutes of inactivity.** The first
  request after that takes ~30-60 seconds to cold-start while it spins back
  up. If a recruiter clicks the link and it looks slow/broken at first,
  that's why — it isn't actually broken.
- **freesqldatabase.com makes no uptime guarantees** — it's built for exactly
  this use case (demos, learning, testing), not production traffic. Fine for
  a portfolio link, not something to rely on for anything real. If it ever
  becomes unreliable or the domain changes hands again, ask me to switch the
  demo to a self-contained SQLite version instead (no third-party DB
  dependency at all) — that's a known fallback, not a from-scratch redo.

## Once it's live

Send me the URL and I'll wire it into the homepage card and report.html as
a "Live Demo" link.
