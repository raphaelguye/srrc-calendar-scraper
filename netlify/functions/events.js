const fetch = require('node-fetch');

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
    const releaseResponse = await fetch(
      'https://api.github.com/repos/raphaelguye/srrc-calendar-scraper/releases/latest'
    );
    
    if (!releaseResponse.ok) {
      throw new Error(`GitHub API error: ${releaseResponse.status}`);
    }
    
    const release = await releaseResponse.json();
    
    // Find the JSON asset
    const jsonAsset = release.assets.find(asset => asset.name === 'srrc_events.json');
    if (!jsonAsset) {
      throw new Error('Events data file not found in latest release');
    }
    
    // Fetch the actual events data from the asset URL
    const eventsResponse = await fetch(jsonAsset.browser_download_url);
    if (!eventsResponse.ok) {
      throw new Error(`Failed to fetch events: ${eventsResponse.status}`);
    }
    
    const eventsData = await eventsResponse.json();
    
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