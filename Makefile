.PHONY: help setup run clean install test

help:
	@echo "SRRC Event Scraper - Available commands:"
	@echo ""
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make install  - Install dependencies in existing virtual environment"
	@echo "  make run      - Run the scraper"
	@echo "  make clean    - Remove virtual environment and generated files"
	@echo "  make all      - Setup and run (complete workflow)"
	@echo ""

setup:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete!"

install:
	@echo "Installing dependencies..."
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

run:
	@echo "Running scraper..."
	./venv/bin/python srrc_event_scraper.py

all: setup run

clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -f srrc_events.json
	rm -rf __pycache__/
	@echo "✅ Cleaned!"
