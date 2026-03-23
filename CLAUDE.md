# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ParliamentWatch** tracks Indian Parliamentary Committee reports from sansad.in. It scrapes report metadata via the sansad.in REST API, downloads PDFs, extracts text, and summarizes key findings using the Claude API. Works without an API key (shows text preview instead of AI summary).

## Architecture

```
cli.py           → Entry point (argparse CLI)
scraper.py       → Fetches report metadata from sansad.in API + search
pdf_utils.py     → Downloads PDFs and extracts text (pypdf)
summarizer.py    → Summarizes reports via Claude API (with text preview fallback)
notifier.py      → Detects new reports, formats email notifications
exporter.py      → Exports data to CSV or Markdown
config.py        → Committee mappings, API codes, paths (loaded from .env)
```

**Data flow:** `scraper.py` → `data/reports.json` → `pdf_utils.py` → `data/text/` → `summarizer.py` → `data/summaries/`

## Key Technical Details

- **sansad.in API**: `GET /api_ls/committee/lsRSAllReports` with params `house` (L/R), `committeeCode`, `lsNo`, `page`, `size`, `sortOn`, `sortBy`. Returns JSON with `records` array and `_metadata`.
- **Committee codes** in `config.py` (`DRSC_COMMITTEES[key]["api_code"]`) map to the API's `committeeCode` param — these are NOT sequential and don't match the URL path numbers.
- **PDF URLs** follow the pattern: `https://sansad.in/getFile/app/lsscommittee/{Committee}/{lsNo}_{Committee}_{ReportNo}.pdf?source=app`
- **House support**: `house=L` for Lok Sabha, `house=R` for Rajya Sabha — same API, same committee codes.
- All data is cached: PDFs in `data/pdfs/`, extracted text in `data/text/`, summaries in `data/summaries/`.
- Config values load from `.env` via python-dotenv. Paths default to `{script_dir}/data/`.

## Common Commands

```bash
source .venv/bin/activate

# Discovery
python cli.py --list-committees              # List all 16 DRSCs
python cli.py --committee defence            # Browse all reports for a committee
python cli.py --search "budget"              # Search report titles across all committees
python cli.py --search "grants" --committee finance  # Search within one committee

# Query a specific report (downloads PDF, extracts text, summarizes or previews)
python cli.py --committee defence --report 23

# Scraping
python cli.py --scrape                       # Scrape all committees (current LS)
python cli.py --scrape --committees defence,finance
python cli.py --scrape --lok-sabha 17        # Historical Lok Sabha
python cli.py --scrape --house R             # Rajya Sabha committees

# Export
python cli.py --export csv                   # All reports to data/reports.csv
python cli.py --export markdown --committee finance  # One committee to data/reports.md

# Monitoring
python cli.py --check-new                    # Detect new reports vs stored data
python cli.py --check-new --committees defence,finance
```

## Setup

1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and configure:
   - `LLM_PROVIDER` — `anthropic` (default) or `openai` (also works for Gemini, Ollama, etc.)
   - `LLM_API_KEY` — API key for the chosen provider (falls back to `ANTHROPIC_API_KEY`)
   - `LLM_MODEL` — model name (defaults: `claude-sonnet-4-20250514` for Anthropic, `gpt-4o` for OpenAI)
   - `LLM_BASE_URL` — custom endpoint for OpenAI-compatible APIs (Gemini, Ollama, LM Studio)
   - `NOTIFICATION_EMAIL` / `SENDER_EMAIL` — for email alerts
   - `LOK_SABHA_NUMBER` — defaults to 18
   - `DATA_DIR` — custom data storage path

## API Response Schema

Each record from the sansad.in API has these fields:
- `url` / `urlH` — PDF download links (English / Hindi)
- `SubjectOfTheReport` / `SubjectOfTheReportH` — report title
- `reportNo` — integer report number
- `CommitteeName` / `CommitteeNameH` — committee name
- `Loksabha` — Lok Sabha number (e.g. 18)
- `PresentedInLS` / `LaidInRS` — date strings like "18-Mar-2026"
- `PresentedToSpeaker`, `dateOfAdoption`, `dateOfPresentation` — often null

## Known Limitations

- **Flat storage by committee key**: `data/reports.json` is keyed by committee name. Scraping a different Lok Sabha (`--lok-sabha 17`) overwrites the same key. Historical data is not preserved alongside current data.
- **Title-only search**: `--search` matches against report titles, not full-text PDF content. The Streamlit app supports full-text search across extracted reports.

## Email Notifications

Automated monitoring runs via GitHub Actions (`.github/workflows/check-reports.yml`):
- Runs daily at 10:00 AM IST
- Checks sansad.in for new reports, compares against stored data
- Sends email via SMTP if new reports are found
- Commits updated `data/reports.json` back to the repo

**GitHub Secrets required:** `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `NOTIFICATION_EMAIL`

Manual email can also be sent via Claude Code's Google Workspace MCP integration (pranay@takshashila.org.in).
