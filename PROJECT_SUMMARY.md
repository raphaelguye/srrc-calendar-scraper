# SRRC Event Scraper - Project Summary

## 🎯 What This Project Does

This project fetches **all events** from the SRRC (Swiss Rock'n'Roll Confederation) calendar at https://srrc.ch/calendrier/

The website uses dynamic loading (AJAX) to show events, so you can't see them all at once. This scraper automatically fetches all events by calling the same AJAX endpoint the "Load More" button uses.

## 📁 Files Included

| File | Purpose |
|------|---------|
| `srrc_event_scraper.py` | Main Python script that does the scraping |
| `requirements.txt` | Python package dependencies |
| `setup_and_run.sh` | Bash script to automate setup and running |
| `Makefile` | Convenience commands for common tasks |
| `README.md` | Full technical documentation |
| `QUICKSTART.md` | Quick start guide for users |
| `sample_output.json` | Example of output format |
| `.gitignore` | Git ignore rules for version control |

## 🚀 How to Use

**Simplest method:**
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

This will:
1. Create a Python virtual environment (isolates dependencies)
2. Install required packages (requests, beautifulsoup4, lxml)
3. Run the scraper
4. Save all events to `srrc_events.json`

## 📊 What You Get

### Console Output
- Real-time progress showing which months are being scanned
- Count of events found per month
- Formatted display of all events with:
  - 📅 Date and day of week
  - Title
  - 📍 Location
  - 👥 Organizer
  - 🗓️ Start and end dates
  - 🔗 URL to event page
  - ℹ️ Description

### JSON Output File
A structured JSON file (`srrc_events.json`) containing all event data that you can:
- Import into other applications
- Parse with scripts
- Convert to other formats (CSV, Excel, etc.)

## 🔧 Technical Details

### How It Works

1. **Date Range Generation**: Scans 24 months forward from current date
2. **AJAX Calls**: Makes POST requests to `https://srrc.ch/wp-admin/admin-ajax.php`
3. **Pagination**: Automatically handles pagination using the `offset` parameter
4. **HTML Parsing**: Extracts event details from returned HTML
5. **Duplicate Removal**: Ensures each event appears only once
6. **Structured Data**: Also parses JSON-LD metadata when available

### AJAX Endpoint

```
URL: https://srrc.ch/wp-admin/admin-ajax.php
Method: POST
Parameters:
  - action: mec_list_load_more
  - mec_start_date: YYYY-MM-DD
  - mec_offset: N (pagination)
  - atts[id]: 0
  - current_month_divider: YYYYMM
  - apply_sf_date: 0
```

## 🎓 What You Learned from the HAR File

The HAR (HTTP Archive) file you provided showed:
- The exact AJAX endpoint used by the website
- Request parameters and their format
- Response structure (JSON with HTML content)
- How pagination works (`has_more_event` flag)

This reverse-engineering allowed us to create a scraper that mimics the browser's behavior.

## 🔍 Events Found So Far

From initial analysis, we identified events in:
- **November 2025**: 5 events (including RA Thurgi Cup, Swiss Ranking Final)
- **December 2025**: 1 event (World Cup Final - Krakow)
- **March 2026**: 1 event (WRRC General Meeting)
- **April 2026**: 2 events (World Cup competitions)
- **May 2026**: 2 events (SRRC Cup, RA Thurgi Cup)
- **November 2026**: 2 events (World Championship - Klagenfurt)

The scraper will find all events across the full date range!

## 🐍 Why Virtual Environment?

Using `venv` (virtual environment) is a Python best practice because:
- **Isolation**: Dependencies don't conflict with system Python
- **Reproducibility**: Anyone can recreate the exact environment
- **Clean**: Easy to remove (just delete the `venv/` folder)
- **Professional**: Standard in production environments

## 🎯 Next Steps

1. Download all files to a local directory
2. Run `./setup_and_run.sh` or `make all`
3. Check `srrc_events.json` for results
4. Optionally modify the script to:
   - Export to CSV format
   - Filter by location or organizer
   - Send notifications for new events
   - Integrate with calendar apps

## 📝 Notes

- The scraper respects the website's structure and doesn't overload it
- It uses the same endpoint as the website's "Load More" button
- All event data comes from official SRRC sources
- The script can be run multiple times to get updated events

## 🤝 Support

For detailed instructions, see:
- **QUICKSTART.md** - Quick start guide
- **README.md** - Full technical documentation
- Script comments - Inline documentation in the code

Enjoy your automated SRRC event collection! 🎉
