#!/usr/bin/env python3
"""
SRRC Calendar Event Scraper
============================
This script fetches all events from the SRRC (Swiss Rock'n'Roll Confederation) calendar
by systematically querying their AJAX endpoint used for the "Load More" functionality.

Usage:
    python3 srrc_event_scraper.py

Output:
    - Prints all events to console
    - Saves events to 'srrc_events.json'
    - Optionally saves to CSV format

Requirements:
    pip install requests beautifulsoup4
"""

import requests
import json
from html import unescape
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys

class SRRCEventScraper:
    def __init__(self):
        self.base_url = "https://srrc.ch/wp-admin/admin-ajax.php"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def fetch_events_page(self, start_date, offset=0):
        """Fetch a page of events from the AJAX endpoint"""
        # Extract year and month from start_date (format: YYYY-MM-DD)
        year_month = start_date[:7].replace('-', '')
        
        data = {
            'action': 'mec_list_load_more',
            'mec_start_date': start_date,
            'mec_offset': str(offset),
            'atts[id]': '0',
            'current_month_divider': year_month,
            'apply_sf_date': '0'
        }
        
        try:
            response = self.session.post(self.base_url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error fetching {start_date} (offset {offset}): {e}", file=sys.stderr)
            return None
    
    def parse_event_html(self, html_content):
        """Parse event information from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        events = []
        
        # Find all event articles
        articles = soup.find_all('article', class_='mec-event-article')
        
        for article in articles:
            try:
                event = {}
                
                # Extract date
                date_div = article.find('div', class_='mec-event-date')
                if date_div:
                    day = date_div.find('div', class_='event-d')
                    month = date_div.find('div', class_='event-f')
                    weekday = date_div.find('div', class_='event-da')
                    
                    event['date_display'] = day.text.strip() if day else ''
                    event['month'] = month.text.strip() if month else ''
                    event['weekday'] = weekday.text.strip() if weekday else ''
                
                # Extract title and link
                title_tag = article.find('h4', class_='mec-event-title')
                if title_tag:
                    link_tag = title_tag.find('a')
                    event['title'] = unescape(link_tag.text.strip()) if link_tag else ''
                    event['url'] = link_tag.get('href', '') if link_tag else ''
                    event['event_id'] = link_tag.get('data-event-id', '') if link_tag else ''
                
                # Extract location
                location_div = article.find('div', class_='mec-event-loc-place')
                event['location'] = location_div.text.strip() if location_div else ''
                
                # Try to extract structured data from JSON-LD
                json_ld_script = article.find_previous('script', type='application/ld+json')
                if json_ld_script:
                    try:
                        structured_data = json.loads(json_ld_script.string)
                        event['start_date'] = structured_data.get('startDate', '')
                        event['end_date'] = structured_data.get('endDate', '')
                        event['description'] = structured_data.get('description', '')
                        
                        # Extract organizer
                        organizer = structured_data.get('organizer', {})
                        if isinstance(organizer, dict):
                            event['organizer'] = organizer.get('name', '')
                    except:
                        pass
                
                events.append(event)
                
            except Exception as e:
                print(f"⚠️  Error parsing event: {e}", file=sys.stderr)
                continue
        
        return events
    
    def generate_date_ranges(self):
        """Generate date ranges to query"""
        # Start from current month and go forward 24 months
        current_date = datetime.now().replace(day=1)
        date_ranges = []
        
        for i in range(24):
            date = current_date + timedelta(days=30*i)
            date_str = date.strftime('%Y-%m-01')
            date_ranges.append(date_str)
        
        return date_ranges
    
    def fetch_all_events(self):
        """Fetch all events from the calendar"""
        all_events = []
        date_ranges = self.generate_date_ranges()
        
        print(f"🔍 Scanning {len(date_ranges)} date ranges...\n")
        
        for start_date in date_ranges:
            offset = 0
            events_in_range = 0
            
            while True:
                result = self.fetch_events_page(start_date, offset)
                
                if not result:
                    break
                
                # Check if there are more events
                has_more = result.get('has_more_event', 0)
                html = result.get('html', '')
                count = result.get('count', 0)
                
                if html and html.strip():
                    events = self.parse_event_html(html)
                    all_events.extend(events)
                    events_in_range += len(events)
                
                if has_more == 0 or count == 0:
                    break
                
                offset += 1
                
                # Safety check
                if offset > 20:
                    print(f"⚠️  Warning: Reached max offset for {start_date}", file=sys.stderr)
                    break
            
            if events_in_range > 0:
                print(f"✓ {start_date}: Found {events_in_range} events")
        
        return all_events
    
    def remove_duplicates(self, events):
        """Remove duplicate events based on event_id or title+date"""
        seen = set()
        unique_events = []
        
        for event in events:
            # Try to use event_id first, fall back to title+start_date
            key = event.get('event_id')
            if not key:
                key = (event.get('title', ''), event.get('start_date', ''))
            
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def format_event_display(self, event):
        """Format an event for console display"""
        lines = []
        
        # Date and title
        date_str = f"{event.get('date_display', '')} {event.get('month', '')} ({event.get('weekday', '')})"
        lines.append(f"📅 {date_str}")
        lines.append(f"   {event.get('title', 'Untitled')}")
        
        # Location
        if event.get('location'):
            lines.append(f"   📍 {event['location']}")
        
        # Organizer
        if event.get('organizer'):
            lines.append(f"   👥 {event['organizer']}")
        
        # Dates (if available)
        if event.get('start_date'):
            lines.append(f"   🗓️  {event['start_date']} → {event.get('end_date', event['start_date'])}")
        
        # URL
        if event.get('url'):
            lines.append(f"   🔗 {event['url']}")
        
        # Description (truncated)
        if event.get('description'):
            desc = event['description']
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"   ℹ️  {desc}")
        
        return '\n'.join(lines)

def main():
    print("=" * 80)
    print("SRRC Calendar Event Scraper")
    print("=" * 80)
    print()
    
    scraper = SRRCEventScraper()
    
    # Fetch all events
    events = scraper.fetch_all_events()
    
    if not events:
        print("\n❌ No events found!")
        return
    
    # Remove duplicates
    unique_events = scraper.remove_duplicates(events)
    
    print(f"\n📊 Total events found: {len(events)}")
    print(f"📊 Unique events: {len(unique_events)}")
    print("\n" + "=" * 80)
    print("EVENTS LIST")
    print("=" * 80)
    print()
    
    # Display events
    for i, event in enumerate(unique_events, 1):
        print(scraper.format_event_display(event))
        print()
    
    # Save to JSON
    output_file = 'srrc_events.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_events, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print(f"✅ Events saved to: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
