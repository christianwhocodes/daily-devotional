# 📖 Daily Devotional Scraper

A GitHub Actions-powered scraper that collects daily devotionals from [joncourson.com](https://www.joncourson.com), stores them in JSON format, and optionally deploys them to GitHub Pages as a static site.

---

## 🌍 Live Site (optional)

> [https://daily-devotional.christianwhocodes.space](https://daily-devotional.christianwhocodes.space)

---

## 🗂️ Project Structure

```
.
├── .github/workflows/scrape-devotional.yml  # GitHub Actions workflow
├── scripts/
│   └── scrape_devotional.py                 # Main scraper logic
├── data/
│   ├── latest.json                          # Most recent devotional
│   └── devotionals.json                     # All devotionals (up to 365)
├── index.html                               # Static site frontend
├── pyproject.toml                           # Poetry dependency config
├── .gitignore                               # Git exclusions (includes .venv)
└── README.md                                # You're reading this
```

---

## ⚙️ Features

- ✅ **Scheduled scraping** via GitHub Actions (1 PM Nairobi / 10 AM UTC)
- ✅ Saves content in structured JSON (`data/latest.json`, `data/devotionals.json`)
- ✅ Smart deduplication and updating of devotionals
- ✅ Simple, readable HTML frontend (auto-updated)
- ✅ Optional deployment to GitHub Pages
- ✅ No servers or cron jobs — GitHub handles everything

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/christianwhocodes/scraper-daily-devotional.git
cd scraper-daily-devotional
```

### 2. Install dependencies (using Poetry)

```bash
poetry install
```

### 3. Run the scraper locally

```bash
poetry run python scripts/scrape_devotional.py
```

---

## 🛠️ GitHub Actions

- The workflow runs daily at **10:00 UTC** (which is **1:00 PM EAT**)
- You can also manually trigger it from the GitHub Actions tab using the **"Run workflow"** button
- It:
  - Scrapes the latest devotional
  - Updates `data/` files
  - Commits and pushes changes (if any)
  - Deploys to GitHub Pages (optional)

---

## 📦 Dependencies

Managed via [Poetry](https://python-poetry.org):

```toml
requests
beautifulsoup4
lxml
```

All defined in `pyproject.toml`.

---

## 🧠 Notes

- The scraper uses CSS selectors based on the current structure of `joncourson.com`. If the website structure changes, you’ll need to update the parser in `scrape_devotional.py`.
- UTF-8 encoding is enforced for JSON output
- The static site fetches devotional data with plain JavaScript

---

## 🛡️ License

This project is for personal and spiritual use. Respect the content author's original copyright.
