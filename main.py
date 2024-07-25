from machine import I2C, Pin, Timer
from time import gmtime, time, sleep

from timing import timeit

# Drivers for the RTC and the display!
# Credit: https://github.com/mcauser/micropython-tinyrtc-i2c
from ds1307 import DS1307

# Credit: https://github.com/T-622/RPI-PICO-I2C-LCD
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

#import weather

sleep(0.1) # Wait for USB to become ready

#weather.connect_wifi()
#weather.fetch_weather()

month_name = ["", "Jan", "Feb", "Mar", "Apr",
              "May", "Jun", "Jul","Aug", "Sept",
              "Oct", "Nov", "Dec"]

# As far as I understand the pi should get accurate
# time from a time server, from which it will set it
# but for in the simulator I'll comment it out
# ds1307.datetime = gmtime(time())


# Setup RTC clock
rtc_clock = I2C(0, scl=Pin(9), sda=Pin(8), freq=800000)
ds1307 = DS1307(addr=0x68, i2c=rtc_clock)

# Setup the display to print everything to!
display = I2C(1, scl=Pin(3), sda=Pin(2), freq=800000)
lcd = I2cLcd(display, 0x27, 2, 16)

lcd.custom_char(1, bytearray([0x0E,0x0A,0x0E,0x00,
0x00,0x00,0x00,0x00]))

# get time! THE TIME!
# formatted as str so I can directly display
# convert 24hr time => 12 hr time
def get_time():
    hour = ds1307.hour
    period = "AM"

    if hour > 12:
        hour -= 12
        period = "PM"
    elif hour == 0:
        hour = 12  # Account for midnight
    elif hour == 12:
        period = "PM"

    return f"{hour:02d}:{ds1307.minute:02d}:{ds1307.second:02d} {period}"


def get_date():
  return f"{month_name[ds1307.month]} {ds1307.day}, {ds1307.year}"

while True:
  lcd.clear()

  for _ in range(50):
    timer = time()
    lcd.move_to(0,0)
    lcd.putstr(get_date())
    if (ds1307.hour == 0) and (ds1307.minute == 0): 
      lcd.move_to(0,0)
      lcd.putstr(get_date())

    lcd.move_to(0,1)
    lcd.putstr(get_time())


    sleep(max(0, 1 - (timer - time())))


  lcd.clear()

  lcd.move_to(0,0)
  lcd.putstr(f"32{chr(1)}c  50%")
  lcd.move_to(0,1)
  lcd.putstr("Partly Cloudly")

  sleep(10)
