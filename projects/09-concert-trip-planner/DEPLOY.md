# Deploying ConcertNOW live

Everything technical is ready in `deploy/` — schema, seed data, production
config. What's left needs your own accounts (I can't sign up for services on
your behalf). Should take about 15 minutes total.

## 1. Database — db4free.net (free MySQL, no card, no expiry)

1. Go to **https://www.db4free.net/signup.php** and register. You'll pick a
   database name and password during signup — write them down.
2. Wait for the confirmation email (usually a couple minutes) and click the
   activation link. Your database isn't usable until you activate it.
3. Load the schema, triggers, stored procedures, and seed data — from your
   terminal, from this `deploy/` folder:
   ```bash
   mysql -h db4free.net -P 3306 -u YOUR_DB4FREE_USERNAME -p YOUR_DB4FREE_DBNAME < setup.sql
   ```
   (It'll prompt for the password you set at signup.) If you'd rather not
   use a terminal, db4free's phpMyAdmin also works, but run the trigger and
   stored procedure sections separately from the table-creation section —
   phpMyAdmin's web SQL box is unreliable with the `DELIMITER $$` blocks
   those need.
4. Verify it worked:
   ```bash
   mysql -h db4free.net -P 3306 -u YOUR_DB4FREE_USERNAME -p YOUR_DB4FREE_DBNAME -e "SHOW TABLES; SELECT * FROM VENUE;"
   ```
   You should see 7 tables and 4 seeded venues.

## 2. Push this repo to GitHub

If you haven't already:
```bash
git remote add origin https://github.com/wen11235/<your-repo-name>.git
git push -u origin main
```

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
4. Under **Environment Variables**, add these 5 (values from step 1):
   | Key | Value |
   |---|---|
   | `DB_HOST` | `db4free.net` |
   | `DB_PORT` | `3306` |
   | `DB_DATABASE` | your db4free database name |
   | `DB_USER` | your db4free username |
   | `DB_PASSWORD` | your db4free password |
5. **Create Web Service**. First deploy takes a few minutes — watch the
   build log for errors.
6. Once live, Render gives you a URL like
   `https://concertnow-xxxx.onrender.com`. Test it: try logging in with the
   seeded demo account (`5551234567` / `demo1234`), search concerts in
   "San Francisco" on `2026-08-02`, check the Community page.

## Known limitations, worth knowing about (both free-tier things, not bugs)

- **Render free tier spins down after 15 minutes of inactivity.** The first
  request after that takes ~30-60 seconds to cold-start while it spins back
  up. If a recruiter clicks the link and it looks slow/broken at first,
  that's why — it isn't actually broken.
- **db4free.net makes no uptime guarantees** — it's built for exactly this
  use case (demos, learning, testing), not production traffic. Fine for a
  portfolio link, not something to rely on for anything real.

## Once it's live

Send me the URL and I'll wire it into the homepage card and report.html as
a "Live Demo" link.
