# A custom written api to fetch the weather easily
# Thanks to https://wokwi.com/projects/365324864723088385
# for the help w/ setting up the wifi simulator!

import rp2
import uasyncio as asyncio
import network
import ubinascii
import machine
import urequests as requests
import time

from timing import timeit

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

weather_str = {}  # <= TODO: Weather info goes there

# Wifi network password here!
ssid = "Wokwi-GUEST"
pw = ''
# End network password stuff

url = "https://api.open-meteo.com/v1/forecast?latitude=43.7001&longitude=-79.4163&current=precipitation,weather_code&timezone=America%2FNew_York&forecast_days=1"

code_names = weather_codes = {
    "0": "Clear Sky",
    "1": "Mainly Clear",
    "2": "Partly Cloudy",
    "3": "Overcast",
    "45": "Fog",
    "48": "Rime fog",
    "51": "Light Drizzle",
    "53": "Moderate Drizzle",
    "55": "Dense Drizzle",
    "56": "Light Frzing Drzle",
    "57": "Dense Frzing Drzle",
    "61": "Slight Rain",
    "63": "Moderate Rain",
    "65": "Heavy Rain",
    "66": "Light Frzing Rain",
    "67": "Hvy Frzing Rain",
    "71": "Slight Snow",
    "73": "Moderate Snow",
    "75": "Heavy Snow",
    "77": "Snow Grains",
    "80": "Slight Rain Showers",
    "81": "Moderate Rain Showers",
    "82": "Violent Rain showers",
    "85": "Slight Snow showers",
    "86": "Heavy Snow showers",
    "95": "Slight/Moderate T-storm",
    "96": "T-storm w/ slight hail",
    "99": "T-storm w/ heavy hail"
}


@timeit
async def connect_wifi():
  attempt_count = 0
  while wlan.status() != 3: # Check if connected
    attempt_count += 1
    print('Connecting to {}. Attempt #{}.'.format(ssid, attempt_count))
    wlan.connect(ssid, pw)
    time.sleep(3)

  status = wlan.ifconfig()
  print('ip = {}'.format(status[0]))


# In a real raspberry Pi apperently you can set a cron job which
# would update the weather readings by calling this func every
# few minutes. But this is a sim so im not gonna update to 
# improve performance lolol. this sim is sloooooow!
@timeit
async def fetch_weather():
  if wlan.status() != 3:
    asyncio.run(connect_wifi())
   
  print('Starting request...')
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()["current"]

    weather_str["weather_code"] = code_names[data["weather_code"]]
    weather_str["precipitation"] = data["precipitation"]

    response.close()
  else:
    print("aw no HTTP 200 - {}".format(response.text))


# get the weather without making an api request
# EVERY. SINGLE. TIME!!!
@timeit
def get_weather():
  if not weather_str:
    asyncio.run(fetch_weather())

  return weather_str
