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

weather_str = None  # <= TODO: Weather info goes there

# Wifi network password here!
ssid = "Wokwi-GUEST"
pw = ''
# End network password stuff


url = "https://api.open-meteo.com/v1/forecast?latitude=43.7001&longitude=-79.4163&current=precipitation,weather_code&timezone=America%2FNew_York&forecast_days=1"


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
    weather_str = response.json()
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
