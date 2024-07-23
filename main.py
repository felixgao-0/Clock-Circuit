from machine import I2C, Pin, Timer
from time import gmtime, time, sleep

# Drivers for the RTC and the display!
from ds1307 import DS1307
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

sleep(0.1) # Wait for USB to become ready

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


# get time! THE TIME!
# formatted as str so I can directly display
def get_time():
  # convert 24hr time => 12 hr time
  if ds1307.hour > 12:
    hour = ds1307.hour - 12
    period = "PM"
  else:
    hour = ds1307.hour
    period = "AM"

  return "{:02d}:{:02d}:{:02d} {}".format(
    hour,
    ds1307.minute,
    ds1307.second,
    period
  )

# get the date ofc
# formatted as str so I can directly display
def get_date():
  return "{} {}, {}".format(
    month_name[ds1307.month],
    ds1307.day,
    ds1307.year
  )


last_date = None
last_time = None


update_count = 0
while True:
  update_count = 0
  lcd.clear()
  lcd.putstr(get_date())
  lcd.move_to(0,1)
  lcd.putstr(get_time())

  while update_count < 50:
    current_date = get_date()
    if current_date != last_date:
      lcd.move_to(0,0)
      lcd.putstr(current_date)
      last_date = current_date
  
    current_time = get_time()
    if current_time != last_time:
      lcd.move_to(0,1)
      lcd.putstr(current_time)
      last_time = current_time

    update_count += 1
    sleep(0.2)
    
  update_count = 0
  lcd.clear()

  while update_count < 50:
    lcd.move_to(0,0)
    lcd.putstr("32°c  50%")
    lcd.move_to(0,1)
    lcd.putstr("Partly Cloudly")

    update_count += 1
    sleep(0.2)
