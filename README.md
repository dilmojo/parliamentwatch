# ParliamentWatch

Track, search, and summarize Indian Parliamentary Committee reports from [sansad.in](https://sansad.in).

ParliamentWatch pulls report metadata via the Sansad API, downloads PDFs, extracts text, and optionally generates AI-powered summaries using Claude. It covers all 16 Departmentally Related Standing Committees (DRSCs) across both Lok Sabha and Rajya Sabha.

## What You Can Do

- **Browse** all reports for any parliamentary committee
- **Search** report titles by keyword (e.g., "budget", "defence procurement")
- **Download and read** committee report PDFs with automatic text extraction
- **Summarize** reports using Claude AI (or view a text preview without an API key)
- **Monitor** committees for newly published reports
- **Export** report metadata to CSV or Markdown
- **Query historical data** from previous Lok Sabhas

## Quick Start

```bash
git clone https://github.com/pranaykotasthane/parliamentwatch.git
cd parliamentwatch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Launch the Web App

```bash
streamlit run app.py
```

This opens a browser-based interface where you can:

1. **Fetch data** — click "Fetch All Committees" in the sidebar to pull reports from sansad.in
2. **Browse Committees** — select a committee and see all its reports in a sortable table
3. **Search Reports** — search by keyword across all committees
4. **Read Report** — pick a report, download its PDF, and get an AI summary or text preview
5. **Download Data** — export report metadata as CSV or Markdown

### Or Use the Command Line

```bash
# Download report metadata for all 16 committees
python cli.py --scrape

# Browse a committee's reports
python cli.py --committee defence

# Read and summarize a specific report
python cli.py --committee defence --report 23

# Search by keyword
python cli.py --search "grants"
```

## Configuration

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | No | Enables AI-powered summaries. Get one at [console.anthropic.com](https://console.anthropic.com). Without it, you still get full text previews. |
| `NOTIFICATION_EMAIL` | No | Email address to receive new-report alerts |
| `SENDER_EMAIL` | No | Email address alerts are sent from |
| `LOK_SABHA_NUMBER` | No | Default Lok Sabha to query (default: `18`) |
| `DATA_DIR` | No | Where to store downloaded data (default: `./data`) |

## Web App Guide

### Browse Committees

Select any committee from the dropdown to see a sortable table of all its reports with report numbers, subjects, and presentation dates. Quick stats show the total count and date range.

### Search Reports

Type a keyword to search across all report titles. Optionally filter by a specific committee. Results show the committee, report number, and title for each match.

### Read Report

1. Select a committee and report from the dropdowns
2. See the report metadata and PDF download links (English and Hindi)
3. Click **Extract Text & Summarize** to:
   - Download the PDF (cached locally)
   - Extract the full text
   - Generate an AI summary (with `ANTHROPIC_API_KEY`) or show a text preview (without it)

### Download Data

Export all report metadata as:
- **CSV** — for analysis in Excel, Google Sheets, R, or Python
- **Markdown** — for documentation or sharing

Filter by committee before downloading to get a focused dataset.

### Update Data

Use the sidebar controls to:
- Switch between **Lok Sabha** and **Rajya Sabha**
- Choose a specific **Lok Sabha number** (e.g., 17 for the previous parliament)
- Click **Fetch All Committees** to pull the latest data from sansad.in

## CLI Reference

All features are also available via the command line:

```bash
# Discovery
python cli.py --list-committees
python cli.py --committee defence
python cli.py --search "budget"
python cli.py --search "grants" --committee finance

# Read a specific report
python cli.py --committee defence --report 23

# Scraping
python cli.py --scrape
python cli.py --scrape --committees defence,finance
python cli.py --scrape --house R          # Rajya Sabha
python cli.py --scrape --lok-sabha 17     # Historical

# Export
python cli.py --export csv
python cli.py --export markdown --committee finance

# Monitor for new reports
python cli.py --check-new
python cli.py --check-new --committees defence,finance
```

## How It Works

ParliamentWatch uses the sansad.in REST API (`/api_ls/committee/lsRSAllReports`) to fetch structured report metadata — no web scraping or browser automation needed. Reports include titles, dates, committee names, and direct PDF download URLs.

```
app.py           → Streamlit web interface
cli.py           → Command-line interface
scraper.py       → Fetches metadata from sansad.in API
pdf_utils.py     → Downloads PDFs and extracts text
summarizer.py    → AI summaries via Claude API (with text preview fallback)
notifier.py      → Detects new reports, formats notifications
exporter.py      → CSV and Markdown export
config.py        → Committee-to-API-code mappings, settings
```

All downloaded data is cached locally:
- `data/reports.json` — scraped metadata
- `data/pdfs/` — downloaded PDFs
- `data/text/` — extracted text
- `data/summaries/` — AI-generated summaries

## Committees Covered

All 16 Departmentally Related Standing Committees (DRSCs) of the Indian Parliament:

Agriculture | Chemicals & Fertilizers | Coal, Mines and Steel | Communications and IT | Consumer Affairs | Defence | Energy | External Affairs | Finance | Housing and Urban Affairs | Labour and Textiles | Petroleum & Natural Gas | Railways | Rural Development | Social Justice | Water Resources

## Requirements

- Python 3.9+
- No browser or Selenium needed — uses the sansad.in API directly

## License

MIT
