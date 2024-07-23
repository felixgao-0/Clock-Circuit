# A custom written api to fetch the weather easily

import requests


url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
	"timezone": "America/New_York",
	"forecast_days": 1
}

weather_str = None  # <= TODO: Weather info goes there

def get_weather():
  return weather_str

def fetch_weather():
  x = requests.post(url, json = myobj)
