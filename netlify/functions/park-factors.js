const https = require('https');

exports.handler = async (event, context) => {
  try {
    const parkFactors = await calculateParkFactors();

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(parkFactors)
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ 
        error: 'Failed to calculate park factors',
        details: error.message 
      })
    };
  }
};

function getWeatherData(lat, lon) {
  return new Promise((resolve, reject) => {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - (7 * 24 * 60 * 60 * 1000));
    
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max,precipitation_sum&start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&timezone=America/New_York`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const weatherData = JSON.parse(data);
          resolve(weatherData);
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', (err) => {
      resolve(null);
    });
  });
}

function calculateWeatherAdjustedFactor(baseFactor, weatherData) {
  if (!weatherData || !weatherData.daily) {
    return baseFactor;
  }
  
  const daily = weatherData.daily;
  if (!daily.temperature_2m_max || !daily.windspeed_10m_max) {
    return baseFactor;
  }
  
  // Get recent averages (last 3 days)
  const recentTemps = daily.temperature_2m_max.slice(-3);
  const recentWinds = daily.windspeed_10m_max.slice(-3);
  
  const avgTemp = recentTemps.reduce((a, b) => a + b, 0) / recentTemps.length;
  const avgWind = recentWinds.reduce((a, b) => a + b, 0) / recentWinds.length;
  
  // Weather adjustments
  let tempFactor = 1.0;
  if (avgTemp > 80) {
    tempFactor = 1.02;
  } else if (avgTemp < 50) {
    tempFactor = 0.98;
  }
  
  let windFactor = 1.0;
  if (avgWind > 15) {
    windFactor = 0.97;
  } else if (avgWind < 5) {
    windFactor = 1.01;
  }
  
  const adjustedFactor = baseFactor * tempFactor * windFactor;
  return Math.round(adjustedFactor * 1000) / 1000;
}

async function calculateParkFactors() {
  const ballparks = {
    "Coors Field": {"lat": 39.7559, "lon": -104.9942, "base_hr": 1.255, "base_runs": 1.115},
    "Great American Ball Park": {"lat": 39.0975, "lon": -84.5061, "base_hr": 1.124, "base_runs": 1.034},
    "Yankee Stadium": {"lat": 40.8296, "lon": -73.9262, "base_hr": 1.103, "base_runs": 1.027},
    "Fenway Park": {"lat": 42.3467, "lon": -71.0972, "base_hr": 1.095, "base_runs": 1.019},
    "Camden Yards": {"lat": 39.2840, "lon": -76.6218, "base_hr": 1.089, "base_runs": 1.015},
    "Rogers Centre": {"lat": 43.6414, "lon": -79.3894, "base_hr": 1.082, "base_runs": 1.012},
    "Minute Maid Park": {"lat": 29.7570, "lon": -95.3551, "base_hr": 1.076, "base_runs": 1.008},
    "Angel Stadium": {"lat": 33.8003, "lon": -117.8827, "base_hr": 1.023, "base_runs": 1.003},
    "Chase Field": {"lat": 33.4453, "lon": -112.0667, "base_hr": 1.019, "base_runs": 1.001},
    "Wrigley Field": {"lat": 41.9484, "lon": -87.6553, "base_hr": 1.015, "base_runs": 0.998},
    "Truist Park": {"lat": 33.8907, "lon": -84.4677, "base_hr": 1.012, "base_runs": 0.995},
    "Citizens Bank Park": {"lat": 39.9061, "lon": -75.1665, "base_hr": 1.008, "base_runs": 0.992},
    "Globe Life Field": {"lat": 32.7473, "lon": -97.0815, "base_hr": 1.005, "base_runs": 0.989},
    "Busch Stadium": {"lat": 38.6226, "lon": -90.1928, "base_hr": 1.001, "base_runs": 0.986},
    "Guaranteed Rate Field": {"lat": 41.8300, "lon": -87.6338, "base_hr": 0.998, "base_runs": 0.983},
    "Target Field": {"lat": 44.9817, "lon": -93.2777, "base_hr": 0.995, "base_runs": 0.980},
    "Citi Field": {"lat": 40.7571, "lon": -73.8458, "base_hr": 0.992, "base_runs": 0.977},
    "Progressive Field": {"lat": 41.4959, "lon": -81.6852, "base_hr": 0.989, "base_runs": 0.974},
    "T-Mobile Park": {"lat": 47.5914, "lon": -122.3325, "base_hr": 0.986, "base_runs": 0.971},
    "Comerica Park": {"lat": 42.3390, "lon": -83.0485, "base_hr": 0.983, "base_runs": 0.968},
    "Tropicana Field": {"lat": 27.7682, "lon": -82.6534, "base_hr": 0.980, "base_runs": 0.965},
    "Kauffman Stadium": {"lat": 39.0517, "lon": -94.4803, "base_hr": 0.977, "base_runs": 0.962},
    "Oracle Park": {"lat": 37.7786, "lon": -122.3893, "base_hr": 0.825, "base_runs": 0.894},
    "Petco Park": {"lat": 32.7073, "lon": -117.1566, "base_hr": 0.822, "base_runs": 0.891},
    "Marlins Park": {"lat": 25.7781, "lon": -80.2197, "base_hr": 0.919, "base_runs": 0.948}
  };
  
  const parkFactors = [];
  
  for (const [parkName, data] of Object.entries(ballparks)) {
    try {
      const weatherData = await getWeatherData(data.lat, data.lon);
      
      const adjustedHrFactor = calculateWeatherAdjustedFactor(data.base_hr, weatherData);
      const adjustedRunsFactor = calculateWeatherAdjustedFactor(data.base_runs, weatherData);
      
      let weatherSummary = "Normal conditions";
      if (weatherData && weatherData.daily && weatherData.daily.temperature_2m_max && weatherData.daily.windspeed_10m_max) {
        const recentTemp = weatherData.daily.temperature_2m_max[weatherData.daily.temperature_2m_max.length - 1] || 70;
        const recentWind = weatherData.daily.windspeed_10m_max[weatherData.daily.windspeed_10m_max.length - 1] || 5;
        weatherSummary = `${Math.round(recentTemp)}°F, ${Math.round(recentWind)} mph wind`;
      }
      
      parkFactors.push({
        park: parkName,
        hr_factor: adjustedHrFactor,
        runs_factor: adjustedRunsFactor,
        weather: weatherSummary,
        base_hr_factor: data.base_hr,
        base_runs_factor: data.base_runs
      });
    } catch (error) {
      // If weather fails for this park, use base factors
      parkFactors.push({
        park: parkName,
        hr_factor: data.base_hr,
        runs_factor: data.base_runs,
        weather: "Weather unavailable",
        base_hr_factor: data.base_hr,
        base_runs_factor: data.base_runs
      });
    }
  }
  
  // Sort by HR factor (highest first)
  parkFactors.sort((a, b) => b.hr_factor - a.hr_factor);
  
  return {
    last_updated: new Date().toISOString(),
    park_factors: parkFactors
  };
}