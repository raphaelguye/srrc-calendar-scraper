# SRRC Event Scraper - Quick Start Guide

## 📋 Project Structure

```
srrc-event-scraper/
├── README.md              # Full documentation
├── requirements.txt       # Python dependencies
├── srrc_event_scraper.py  # Main scraper script
├── setup_and_run.sh       # Automated setup and run
├── Makefile               # Convenience commands
└── .gitignore            # Git ignore rules
```

## 🚀 Quick Start

### Method 1: Automated (Easiest)

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Method 2: Using Make

```bash
make all
```

### Method 3: Manual

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run scraper
python srrc_event_scraper.py

# Deactivate when done
deactivate
```

## 📦 What Gets Installed

From `requirements.txt`:
- **requests** - HTTP library for making API calls
- **beautifulsoup4** - HTML parsing library
- **lxml** - Fast XML/HTML parser

## 📤 Output

After running, you'll get:
- **Console output**: Formatted list of all events
- **srrc_events.json**: JSON file with all event data

## 🛠️ Make Commands

If you have `make` installed:

```bash
make help      # Show available commands
make setup     # Create venv and install deps
make run       # Run the scraper
make clean     # Remove venv and output files
make all       # Setup and run in one command
```

## 🔧 Troubleshooting

### "python3: command not found"
Install Python 3 from https://python.org

### "venv: command not found"
Your Python might not include venv. Install it:
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# macOS (using Homebrew)
brew install python3
```

### Permission denied
Make scripts executable:
```bash
chmod +x setup_and_run.sh
```

### SSL Certificate errors
Update certificates:
```bash
# macOS
/Applications/Python\ 3.*/Install\ Certificates.command

# Ubuntu/Debian
sudo apt-get install ca-certificates
```

## 📊 Example Output

```
🔍 Scanning 24 date ranges...

✓ 2025-11-01: Found 5 events
✓ 2025-12-01: Found 1 events
✓ 2026-03-01: Found 1 events
✓ 2026-04-01: Found 2 events
✓ 2026-05-01: Found 2 events
✓ 2026-11-01: Found 2 events

📊 Total events found: 13
📊 Unique events: 13

================================================================================
EVENTS LIST
================================================================================

📅 08 novembre (samedi)
   RA Thurgi Cup 2025
   📍 [Location]
   🔗 https://srrc.ch/events/...

...
```

## 📖 More Information

See README.md for complete documentation including:
- How the AJAX endpoint works
- Request/response format details
- Browser console alternatives
- Event data structure

## 🤝 Support

For questions or issues related to the scraper, check:
1. README.md - Full documentation
2. The code comments in srrc_event_scraper.py
3. SRRC website: https://srrc.ch
