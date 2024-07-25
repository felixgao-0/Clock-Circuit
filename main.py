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


# Setup RTC clock
rtc_clock = I2C(0, scl=Pin(9), sda=Pin(8), freq=800000)
ds1307 = DS1307(addr=0x68, i2c=rtc_clock)

# Setup the display to print everything to!
display = I2C(1, scl=Pin(3), sda=Pin(2), freq=800000)
lcd = I2cLcd(display, 0x27, 2, 16)

# Setup buttons
alarm_btn = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)
hour_btn = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)
minute_btn = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)

# Define custom characters
lcd.custom_char(1, bytearray([0x0E,0x0A,0x0E,0x00,
0x00,0x00,0x00,0x00]))


# As far as I understand the pi should get accurate
# time from a time server, from which it will set it

# Convert to different times for testing lol
#pi_time = list(gmtime(time()))  # convert to list for editing
#pi_time[3] = 10
#pi_time[4] = 59
#pi_time[5] = 50
#ds1307.datetime = tuple(pi_time) # It expects a tuple type lol

def only_ones_changed(prev_time: int, new_time: int):
    if not prev_time: # Handle nonetypes
        return False

    prev_tens_place = prev_time // 10
    prev_ones_place = prev_time % 10
    new_tens_place = new_time // 10
    new_ones_place = new_time % 10

    if prev_tens_place == new_tens_place and prev_ones_place != new_ones_place:
        return True
    elif prev_tens_place != new_tens_place and prev_ones_place != new_ones_place:
        return False
    else:
        raise ValueError("Huh? Didn't expect this to happen")

# get time! THE TIME!
# formatted as str so I can directly display
# convert 24hr time => 12 hr time
def get_hour(dt_obj, get_period=False):
    hour = dt_obj[3]
    period = "AM"

    if hour > 12:
        hour -= 12
        period = "PM"
    elif hour == 0:
        hour = 12  # Account for midnight
    elif hour == 12:
        period = "PM"

    if get_period:
        return period
    else:
        return f"{hour:02d}"


def get_date(dt_obj):
  return f"{month_name[dt_obj[1]]} {dt_obj[2]}, {dt_obj[0]}"

previous_second = None

def set_alarm():
    lcd.clear()

while True:
    previous_second = ds1307.second

    lcd.clear()
    dt_obj = ds1307.datetime

    lcd.move_to(0,0)
    lcd.putstr(get_date(dt_obj))

    lcd.move_to(0,1)
    lcd.putstr(f"{get_hour(dt_obj, get_period=False)}:{dt_obj[4]:02d}:{dt_obj[5]:02d} {get_hour(dt_obj, get_period=True)}")

    while ds1307.second % 10 != 0 or ds1307.second == previous_second:
        dt_obj = ds1307.datetime # Save dt object to avoid too many i2c calls
        if (dt_obj[3] == 0) and (dt_obj[4] == 0): # Update date if time is 12:00 am
            lcd.move_to(0,0)
            lcd.putstr(get_date(dt_obj))
    

        if dt_obj[4] == 0: # Update hour if minutes at 00
            lcd.move_to(0,1)
            lcd.putstr(get_hour(dt_obj, get_period=False))
            lcd.move_to(9,1)
            lcd.putstr(get_hour(dt_obj, get_period=True))


        if dt_obj[5] == 0: # Update minute if seconds at 00
            lcd.move_to(3,1)
            lcd.putstr(f"{dt_obj[4]:02d}")

        if previous_second != dt_obj[5]:
            if only_ones_changed(previous_second, dt_obj[5]):
                lcd.move_to(7,1)
                lcd.putstr(str(dt_obj[5] % 10))
            else:
                lcd.move_to(6,1)
                lcd.putstr(f"{dt_obj[5]:02d}")
        previous_second = dt_obj[5]

        print(alarm_btn.value())
        sleep(0.2)

    lcd.clear()
    previous_second = ds1307.second

    lcd.move_to(0,0)
    lcd.putstr(f"32{chr(1)}c  50%")
    lcd.move_to(0,1)
    lcd.putstr("Partly Cloudly")

    previous_second = ds1307.second

    while ds1307.second % 10 != 0 or ds1307.second == previous_second:
        print(alarm_btn.value())
        sleep(0.2)
