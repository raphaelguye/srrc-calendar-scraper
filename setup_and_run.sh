#!/bin/bash

# SRRC Event Scraper Setup & Run Script
# ======================================
# This script sets up a Python virtual environment and runs the scraper

set -e  # Exit on error

echo "=============================================="
echo "SRRC Calendar Event Scraper"
echo "=============================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 first"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

echo "✓ All dependencies installed"
echo ""

echo "🚀 Starting scraper..."
echo "=============================================="
echo ""

# Run the scraper
python srrc_event_scraper.py

# Check exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ Success! Check srrc_events.json"
    echo "=============================================="
    echo ""
    echo "💡 Tip: To activate the virtual environment manually:"
    echo "   source venv/bin/activate"
else
    echo ""
    echo "=============================================="
    echo "❌ Scraper encountered an error"
    echo "=============================================="
    exit 1
fi
