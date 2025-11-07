# SRRC Calendar Event Scraper

## 🚀 Automated Event Data via GitHub Actions

This project automatically scrapes SRRC events **daily** and makes them available through GitHub Releases for easy integration with mobile applications and other services.

## Overview

The SRRC (Swiss Rock'n'Roll Confederation) website uses a dynamic JavaScript-based calendar that loads events progressively via AJAX calls. This scraper automates the process of collecting all event data by interfacing with the underlying WordPress AJAX endpoint.

## Technical Details

### AJAX Endpoint
- **URL**: `https://srrc.ch/wp-admin/admin-ajax.php`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded`

### Request Parameters
```
action=mec_list_load_more
mec_start_date=YYYY-MM-DD
mec_offset=N
atts[id]=0
current_month_divider=YYYYMM
apply_sf_date=0
```

### Response Format
The endpoint returns JSON with the following structure:
```json
{
  "html": "<html content with events>",
  "end_date": "YYYY-MM-DD",
  "offset": N,
  "count": N,
  "current_month_divider": "YYYYMM",
  "has_more_event": 0 or 1
}
```

## Event Data Structure

The scraper collects comprehensive event information including:

- **Event dates and times**
- **Event titles and descriptions** 
- **Location information**
- **Event organizers**
- **Event URLs and additional details**
- **Event categories** (competitions, training, meetings, etc.)

Events span multiple years and include various types of activities such as:
- Regional and international competitions
- Training sessions and workshops
- Official meetings and assemblies
- Certification and skills assessments

## 🤖 Automated Data Collection (GitHub Actions)

### What Happens Automatically

1. **Daily at 6 AM UTC**: GitHub Actions runs the scraper
2. **Events Scraped**: All events for the next 24 months are collected
3. **Release Created**: New release with `srrc_events.json` file
4. **Mobile Apps**: Can fetch data via GitHub Releases API

### Manual Trigger

You can also trigger the scraper manually:
1. Go to [Actions tab](../../actions)
2. Click "SRRC Event Scraper"
3. Click "Run workflow"

### API Endpoints for Mobile Apps

```bash
# Get latest release info (includes download URLs)
GET https://api.github.com/repos/raphaelguye/srrc-calendar-scraper/releases/latest

# Direct download (URL from above response)
GET https://github.com/raphaelguye/srrc-calendar-scraper/releases/download/TAG/srrc_events.json
```

## 🛠️ Local Development

If you want to run the scraper locally or contribute to the project:

### Option 1: Use the Python Script with Virtual Environment (Recommended)

This project uses a Python virtual environment to keep dependencies isolated.

#### Quick Start (Automated)

1. **Download all files** to a directory
2. **Run the setup script**:
   ```bash
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

This will automatically:
- Create a virtual environment
- Install all dependencies from `requirements.txt`
- Run the scraper
- Save results to `srrc_events.json`

#### Manual Setup

If you prefer to set up manually:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the script**:
   ```bash
   python srrc_event_scraper.py
   ```

5. **Deactivate when done**:
   ```bash
   deactivate
   ```

#### Output
- All events will be printed to console with nice formatting
- Events will be saved to `srrc_events.json`

### Option 2: Use the Python Script (Without Virtual Environment)

If you don't want to use a virtual environment:

1. **Install dependencies globally**:
   ```bash
   pip install requests beautifulsoup4 lxml
   ```

2. **Run the script**:
   ```bash
   python3 srrc_event_scraper.py
   ```

### Alternative: Browser Console Script

Open the browser console on https://srrc.ch/calendrier/ and run:

```javascript
// Function to fetch events
async function fetchAllEvents() {
    const events = [];
    let startDate = '2025-01-01';
    let offset = 0;
    
    while (true) {
        const yearMonth = startDate.substr(0, 7).replace('-', '');
        
        const formData = new URLSearchParams({
            'action': 'mec_list_load_more',
            'mec_start_date': startDate,
            'mec_offset': offset,
            'atts[id]': '0',
            'current_month_divider': yearMonth,
            'apply_sf_date': '0'
        });
        
        const response = await fetch('/wp-admin/admin-ajax.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.count > 0) {
            events.push({
                date: startDate,
                offset: offset,
                html: data.html,
                count: data.count
            });
            console.log(`Found ${data.count} events for ${startDate} (offset ${offset})`);
        }
        
        if (data.has_more_event === 0) {
            // Move to next month
            const date = new Date(startDate);
            date.setMonth(date.getMonth() + 1);
            startDate = date.toISOString().substr(0, 10);
            offset = 0;
            
            // Stop after 24 months
            if (date > new Date(Date.now() + 24*30*24*60*60*1000)) {
                break;
            }
        } else {
            offset++;
        }
    }
    
    console.log('Complete! Found', events.length, 'event pages');
    return events;
}

// Execute the function
fetchAllEvents().then(events => {
    console.log('Scraping complete!');
    // Export results
    console.log('Event data:', JSON.stringify(events, null, 2));
});
```

## Additional Resources

The SRRC website also provides PDF agenda documents that contain official event listings. These documents serve as a complementary source for event information validation.
