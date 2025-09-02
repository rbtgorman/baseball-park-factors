import requests
import json
import os
import sys
from datetime import datetime
import numpy as np
from typing import Dict, List

# MLB Stadium data with coordinates
STADIUMS = {
    'Coors Field': {
        'city': 'Denver', 'state': 'CO', 'team': 'COL', 'elevation': 5200,
        'lat': 39.7559, 'lon': -104.9942
    },
    'Fenway Park': {
        'city': 'Boston', 'state': 'MA', 'team': 'BOS', 'elevation': 21,
        'lat': 42.3467, 'lon': -71.0972
    },
    'Wrigley Field': {
        'city': 'Chicago', 'state': 'IL', 'team': 'CHC', 'elevation': 595,
        'lat': 41.9484, 'lon': -87.6553
    },
    'Yankee Stadium': {
        'city': 'New York', 'state': 'NY', 'team': 'NYY', 'elevation': 55,
        'lat': 40.8296, 'lon': -73.9262
    },
    'Minute Maid Park': {
        'city': 'Houston', 'state': 'TX', 'team': 'HOU', 'elevation': 22,
        'lat': 29.7572, 'lon': -95.3555
    },
    'Globe Life Field': {
        'city': 'Arlington', 'state': 'TX', 'team': 'TEX', 'elevation': 551,
        'lat': 32.7473, 'lon': -97.0833
    },
    'T-Mobile Park': {
        'city': 'Seattle', 'state': 'WA', 'team': 'SEA', 'elevation': 135,
        'lat': 47.5914, 'lon': -122.3326
    },
    'Progressive Field': {
        'city': 'Cleveland', 'state': 'OH', 'team': 'CLE', 'elevation': 660,
        'lat': 41.4962, 'lon': -81.6852
    },
    'Kauffman Stadium': {
        'city': 'Kansas City', 'state': 'MO', 'team': 'KC', 'elevation': 750,
        'lat': 39.0517, 'lon': -94.4803
    },
    'Oriole Park at Camden Yards': {
        'city': 'Baltimore', 'state': 'MD', 'team': 'BAL', 'elevation': 20,
        'lat': 39.2838, 'lon': -76.6218
    },
    'Petco Park': {
        'city': 'San Diego', 'state': 'CA', 'team': 'SD', 'elevation': 62,
        'lat': 32.7073, 'lon': -117.1566
    },
    'Oracle Park': {
        'city': 'San Francisco', 'state': 'CA', 'team': 'SF', 'elevation': 20,
        'lat': 37.7786, 'lon': -122.3893
    },
    'Dodger Stadium': {
        'city': 'Los Angeles', 'state': 'CA', 'team': 'LAD', 'elevation': 340,
        'lat': 34.0739, 'lon': -118.2400
    },
    'Angel Stadium': {
        'city': 'Anaheim', 'state': 'CA', 'team': 'LAA', 'elevation': 160,
        'lat': 33.8003, 'lon': -117.8827
    },
    'Guaranteed Rate Field': {
        'city': 'Chicago', 'state': 'IL', 'team': 'CWS', 'elevation': 595,
        'lat': 41.8300, 'lon': -87.6338
    },
    'Comerica Park': {
        'city': 'Detroit', 'state': 'MI', 'team': 'DET', 'elevation': 585,
        'lat': 42.3391, 'lon': -83.0485
    },
    'Target Field': {
        'city': 'Minneapolis', 'state': 'MN', 'team': 'MIN', 'elevation': 815,
        'lat': 44.9817, 'lon': -93.2777
    },
    'Nationals Park': {
        'city': 'Washington', 'state': 'DC', 'team': 'WSH', 'elevation': 25,
        'lat': 38.8730, 'lon': -77.0074
    },
    'Citi Field': {
        'city': 'New York', 'state': 'NY', 'team': 'NYM', 'elevation': 20,
        'lat': 40.7571, 'lon': -73.8458
    },
    'Citizens Bank Park': {
        'city': 'Philadelphia', 'state': 'PA', 'team': 'PHI', 'elevation': 65,
        'lat': 39.9061, 'lon': -75.1665
    }
}

# Historical park factors (2024 season estimates)
HISTORICAL_PARK_FACTORS = {
    'COL': {'HR': 130, '2B': 120, '1B': 108, 'R': 115},
    'BOS': {'HR': 105, '2B': 115, '1B': 102, 'R': 108},
    'CHC': {'HR': 108, '2B': 105, '1B': 99, 'R': 104},
    'NYY': {'HR': 115, '2B': 98, '1B': 97, 'R': 106},
    'HOU': {'HR': 95, '2B': 92, '1B': 95, 'R': 96},
    'TEX': {'HR': 102, '2B': 96, '1B': 98, 'R': 99},
    'SEA': {'HR': 90, '2B': 92, '1B': 97, 'R': 93},
    'CLE': {'HR': 88, '2B': 94, '1B': 99, 'R': 94},
    'KC': {'HR': 92, '2B': 90, '1B': 95, 'R': 93},
    'BAL': {'HR': 105, '2B': 102, '1B': 98, 'R': 102},
    'SD': {'HR': 85, '2B': 88, '1B': 94, 'R': 89},
    'SF': {'HR': 82, '2B': 90, '1B': 96, 'R': 88},
    'LAD': {'HR': 88, '2B': 92, '1B': 98, 'R': 92},
    'LAA': {'HR': 94, '2B': 96, '1B': 99, 'R': 96},
    'CWS': {'HR': 96, '2B': 98, '1B': 101, 'R': 98},
    'DET': {'HR': 92, '2B': 96, '1B': 100, 'R': 96},
    'MIN': {'HR': 96, '2B': 98, '1B': 102, 'R': 99},
    'WSH': {'HR': 94, '2B': 95, '1B': 99, 'R': 96},
    'NYM': {'HR': 88, '2B': 94, '1B': 98, 'R': 93},
    'PHI': {'HR': 102, '2B': 100, '1B': 97, 'R': 100}
}

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5'
    
    def get_weather_for_stadium(self, lat, lon):
        """Get current weather for stadium coordinates"""
        if not self.api_key:
            print("No weather API key found, using mock data", file=sys.stderr)
            return self.get_mock_weather()
        
        try:
            response = requests.get(f"{self.base_url}/weather", {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Weather API error: {response.status_code}", file=sys.stderr)
                return self.get_mock_weather()
                
        except Exception as e:
            print(f"Weather API error: {e}", file=sys.stderr)
            return self.get_mock_weather()
    
    def get_mock_weather(self):
        """Generate realistic mock weather data"""
        conditions = ['partly cloudy', 'mostly sunny', 'overcast', 'clear', 'light clouds']
        temps = [65, 68, 72, 75, 78, 82, 85]
        
        return {
            'main': {
                'temp': np.random.choice(temps),
                'humidity': np.random.randint(35, 85)
            },
            'wind': {
                'speed': np.random.randint(2, 18),
                'deg': np.random.randint(0, 360)
            },
            'weather': [{'description': np.random.choice(conditions)}]
        }

class ParkFactorCalculator:
    def __init__(self, weather_service):
        self.weather_service = weather_service
    
    def calculate_daily_factors(self):
        """Calculate weather-adjusted park factors for all stadiums"""
        park_factors = []
        
        for ballpark, info in STADIUMS.items():
            try:
                weather = self.weather_service.get_weather_for_stadium(info['lat'], info['lon'])
                base_factors = HISTORICAL_PARK_FACTORS.get(info['team'], 
                    {'HR': 100, '2B': 100, '1B': 100, 'R': 100})
                
                adjusted_factors = self.apply_weather_adjustments(
                    weather, info['elevation'], base_factors)
                
                park_factor = {
                    'ballpark': ballpark,
                    'team': info['team'],
                    'city': info['city'],
                    'state': info['state'],
                    'temperatureRange': self.get_temp_range(weather['main']['temp']),
                    'weatherCondition': weather['weather'][0]['description'],
                    'windDirection': self.get_wind_direction(weather['wind']['deg']),
                    'windSpeed': round(weather['wind']['speed']),
                    'hrFactor': adjusted_factors['HR'],
                    'doublesFactor': adjusted_factors['2B'],
                    'singlesFactor': adjusted_factors['1B'],
                    'runsFactor': adjusted_factors['R'],
                    'overallRating': self.get_overall_rating(adjusted_factors)
                }
                
                park_factors.append(park_factor)
                
            except Exception as e:
                print(f"Error processing {ballpark}: {e}", file=sys.stderr)
                continue
        
        return sorted(park_factors, key=lambda x: x['runsFactor'], reverse=True)
    
    def apply_weather_adjustments(self, weather, elevation, base_factors):
        """Apply weather and elevation adjustments to base park factors"""
        temp = weather['main']['temp']
        humidity = weather['main']['humidity']
        wind_speed = weather['wind']['speed']
        wind_deg = weather['wind']['deg']
        
        # Temperature effect (warmer air = lower density = more HRs)
        temp_adj = 1 + (temp - 70) * 0.002
        
        # Humidity effect (higher humidity = denser air = fewer HRs)
        humidity_adj = 1 - (humidity - 50) * 0.001
        
        # Elevation effect (higher elevation = thinner air = more HRs)
        elevation_adj = 1 + (elevation - 500) * 0.00005
        
        # Wind effect (tailwind helps HRs, headwind hurts)
        # Assume center field is at 0° (north)
        wind_adj = 1 + (wind_speed * np.cos(np.radians(wind_deg - 90))) * 0.01
        
        # Apply adjustments
        hr_adjusted = base_factors['HR'] * temp_adj * humidity_adj * elevation_adj * wind_adj
        doubles_adjusted = base_factors['2B'] * temp_adj * 0.5  # Less weather sensitive
        singles_adjusted = base_factors['1B'] * temp_adj * 0.2  # Least weather sensitive
        runs_adjusted = (hr_adjusted + doubles_adjusted + singles_adjusted) / 3
        
        return {
            'HR': round(hr_adjusted, 1),
            '2B': round(doubles_adjusted, 1),
            '1B': round(singles_adjusted, 1),
            'R': round(runs_adjusted, 1)
        }
    
    def get_temp_range(self, temp):
        """Convert temperature to range string"""
        low = int(temp / 10) * 10
        high = low + 9
        return f"{low}s to {high}s"
    
    def get_wind_direction(self, degrees):
        """Convert wind degrees to cardinal direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def get_overall_rating(self, factors):
        """Calculate overall offensive rating"""
        avg_factor = (factors['HR'] + factors['2B'] + factors['1B']) / 3
        if avg_factor >= 110:
            return "Excellent"
        elif avg_factor >= 105:
            return "Good"
        elif avg_factor >= 95:
            return "Neutral"
        elif avg_factor >= 90:
            return "Below Average"
        else:
            return "Poor"

def main():
    """Main function"""
    try:
        weather_service = WeatherService()
        calculator = ParkFactorCalculator(weather_service)
        
        park_factors = calculator.calculate_daily_factors()
        
        output = {
            'factors': park_factors,
            'lastUpdated': datetime.now().isoformat(),
            'date': datetime.now().strftime('%B %d, %Y'),
            'timestamp': datetime.now().timestamp()
        }
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save to file for static serving
        with open('data/park-factors.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        # Output to stdout for function calls
        print(json.dumps(output, indent=2))
        
        return output
        
    except Exception as e:
        error_output = {
            'error': str(e),
            'factors': [],
            'lastUpdated': datetime.now().isoformat(),
            'date': datetime.now().strftime('%B %d, %Y')
        }
        
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()