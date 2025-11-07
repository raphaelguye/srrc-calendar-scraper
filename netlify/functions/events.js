const https = require('https');

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, {
      headers: {
        'User-Agent': 'SRRC-Events-Scraper/1.0'
      }
    }, (response) => {
      let data = '';
      
      response.on('data', (chunk) => {
        data += chunk;
      });
      
      response.on('end', () => {
        try {
          if (response.statusCode >= 200 && response.statusCode < 300) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`));
          }
        } catch (error) {
          reject(new Error(`JSON parse error: ${error.message}`));
        }
      });
    });
    
    request.on('error', (error) => {
      reject(new Error(`Request error: ${error.message}`));
    });
    
    request.setTimeout(10000, () => {
      request.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

exports.handler = async (event, context) => {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  try {
    // Get the latest release info
    console.log('Fetching GitHub release info...');
    const release = await fetchJson(
      'https://api.github.com/repos/raphaelguye/srrc-calendar-scraper/releases/latest'
    );
    
    // Find the JSON asset
    const jsonAsset = release.assets.find(asset => asset.name === 'srrc_events.json');
    if (!jsonAsset) {
      throw new Error('Events data file not found in latest release');
    }
    
    console.log('Fetching events data from:', jsonAsset.browser_download_url);
    
    // Fetch the actual events data from the asset URL
    const eventsData = await fetchJson(jsonAsset.browser_download_url);
    
    console.log(`Successfully fetched ${Array.isArray(eventsData) ? eventsData.length : 'unknown'} events`);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(eventsData),
    };
    
  } catch (error) {
    console.error('Error in events function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Failed to fetch events data',
        message: error.message 
      }),
    };
  }
};