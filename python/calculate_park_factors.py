#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime, timedelta
from statistics import mean

def get_weather_data(lat, lon, days_back=7):
    """Get weather data from Open-Meteo API"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,windspeed_10m_max,precipitation_sum',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'timezone': 'America/New_York'
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def calculate_weather_adjusted_factor(base_factor, weather_data):
    """Calculate weather-adjusted park factor"""
    if not weather_data or 'daily' not in weather_data:
        return base_factor
    
    daily = weather_data['daily']
    if not daily.get('temperature_2m_max') or not daily.get('windspeed_10m_max'):
        return base_factor
    
    # Get recent averages
    avg_temp = mean(daily['temperature_2m_max'][-3:])  # Last 3 days
    avg_wind = mean(daily['windspeed_10m_max'][-3:])   # Last 3 days
    
    # Weather adjustments (simplified model)
    temp_factor = 1.0
    if avg_temp > 80:  # Hot weather - ball carries farther
        temp_factor = 1.02
    elif avg_temp < 50:  # Cold weather - ball doesn't carry as far
        temp_factor = 0.98
    
    wind_factor = 1.0
    if avg_wind > 15:  # Strong winds
        wind_factor = 0.97  # Generally suppress offense
    elif avg_wind < 5:  # Calm conditions
        wind_factor = 1.01
    
    # Apply adjustments to base factor
    adjusted_factor = base_factor * temp_factor * wind_factor
    return round(adjusted_factor, 3)

def calculate_park_factors():
    """Calculate park factors with weather adjustments"""
    
    # MLB ballpark data with coordinates and base factors
    ballparks = {
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
        "Marlins Park": {"lat": 25.7781, "lon": -80.2197, "base_hr": 0.919, "base_runs": 0.948},
    }
    
    park_factors = []
    
    for park_name, data in ballparks.items():
        # Get weather data for this ballpark
        weather_data = get_weather_data(data['lat'], data['lon'])
        
        # Calculate weather-adjusted factors
        adjusted_hr_factor = calculate_weather_adjusted_factor(data['base_hr'], weather_data)
        adjusted_runs_factor = calculate_weather_adjusted_factor(data['base_runs'], weather_data)
        
        # Get weather summary for display
        weather_summary = "Normal conditions"
        if weather_data and 'daily' in weather_data:
            daily = weather_data['daily']
            if daily.get('temperature_2m_max') and daily.get('windspeed_10m_max'):
                recent_temp = daily['temperature_2m_max'][-1] if daily['temperature_2m_max'] else 70
                recent_wind = daily['windspeed_10m_max'][-1] if daily['windspeed_10m_max'] else 5
                weather_summary = f"{recent_temp}°F, {recent_wind} mph wind"
        
        park_factors.append({
            "park": park_name,
            "hr_factor": adjusted_hr_factor,
            "runs_factor": adjusted_runs_factor,
            "weather": weather_summary,
            "base_hr_factor": data['base_hr'],
            "base_runs_factor": data['base_runs']
        })
    
    # Sort by HR factor (highest first)
    park_factors.sort(key=lambda x: x['hr_factor'], reverse=True)
    
    result = {
        "last_updated": datetime.now().isoformat(),
        "park_factors": park_factors
    }
    
    return result

if __name__ == "__main__":
    try:
        # Calculate park factors
        data = calculate_park_factors()
        
        # Output JSON to stdout (for the Node.js function to read)
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        # Output error as JSON
        error_data = {
            "error": "Failed to calculate park factors",
            "details": str(e)
        }
        print(json.dumps(error_data, indent=2))
        sys.exit(1)