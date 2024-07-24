# A custom written api to fetch the weather easily
# Thanks to https://wokwi.com/projects/365324864723088385
# for the help w/ setting up the wifi simulator!

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = {}'.format(mac))

weather_str = None  # <= TODO: Weather info goes there

# Wifi network password here!
ssid = "Wokwi-GUEST"
pw = ''
# End network password stuff


url = "https://api.open-meteo.com/v1/forecast?latitude=43&longitude=-79&current=temperature_2m,relative_humidity_2m,weather_code&timezone=America%2FNew_York"

def wifi_connected():
    wlan_status = wlan.status()
    if wlan_status != 3:
        return False
    else:
        return True

attempt_count = 0
def connect_wifi():
  while True:
    if wifi_connected():
      status = wlan.ifconfig()
      print('ip = ' + status[0])
      break
    else:
      print('Attempting to connect. Attempt #{}.'.format(attempt_count))
      attempt_count += 1
      led.off()
      wlan.connect(ssid, pw)
      time.sleep(3)


connect_wifi()


def fetch_weather():
  if not wifi_connected():
    connect_wifi()

  response = requests.get(url)
  print(response)
  response.close()

def get_weather():
  return weather_str
