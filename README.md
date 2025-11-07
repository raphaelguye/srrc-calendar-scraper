# SRRC Calendar Event Scraper

## 🚀 Automated Event Data via GitHub Actions

This project automatically scrapes SRRC events **daily** and makes them available through GitHub Releases for easy integration with mobile applications, web apps, and other services.

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
4. **Client Applications**: Can fetch data via GitHub Releases API

### Manual Trigger

You can also trigger the scraper manually:
1. Go to [Actions tab](../../actions)
2. Click "SRRC Event Scraper"
3. Click "Run workflow"

### API Endpoints for Client Applications

```bash
# Get latest release info (includes download URLs)
GET https://api.github.com/repos/raphaelguye/srrc-calendar-scraper/releases/latest

# Direct download (URL from above response)
GET https://github.com/raphaelguye/srrc-calendar-scraper/releases/download/TAG/srrc_events.json
```

## 🌐 Web Interface

A web interface is available to browse events directly in your browser:

**Live Site**: [https://srrc-calendar.netlify.app](https://srrc-calendar.netlify.app)

### Features
- 🔍 **Search and filter** events
- 📱 **Mobile-friendly** responsive design
- 🔄 **Auto-refresh** with latest data
- 📊 **Event statistics** and counters

### Netlify Deployment

The web interface uses Netlify for hosting with CORS proxy configuration:

```toml
# netlify.toml
[build]
  publish = "docs"

[[redirects]]
  from = "/api/releases"
  to = "https://api.github.com/repos/raphaelguye/srrc-calendar-scraper/releases/latest"
  status = 200
  force = true

[[redirects]]
  from = "/api/events.json"
  to = "https://github.com/raphaelguye/srrc-calendar-scraper/releases/latest/download/srrc_events.json"
  status = 200
  force = true
```

This configuration creates API endpoints that bypass CORS restrictions for web browsers.

## 🛠️ Local Development

To run the scraper locally:

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/raphaelguye/srrc-calendar-scraper.git
   cd srrc-calendar-scraper
   ```

2. **Run the automated setup**:
   ```bash
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

This script will automatically:
- Create a Python virtual environment
- Install all required dependencies
- Run the scraper
- Generate `srrc_events.json` with all events

### Output
- All events will be printed to console with formatting
- Events data saved to `srrc_events.json`
- Ready for integration with your applications

## Integration Examples

The generated `srrc_events.json` can be consumed by:
- **Mobile apps** (iOS, Android, React Native, Flutter)
- **Web applications** (React, Vue, Angular, vanilla JS)
- **Desktop applications** (Electron, native apps)
- **Backend services** (Node.js, Python, Java, etc.)
- **Data analysis tools** (R, Python pandas, etc.)

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
