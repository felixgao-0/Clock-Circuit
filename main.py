from ds1307 import DS1307
from machine import I2C, Pin, Timer
from time import gmtime, time, sleep


sleep(0.1) # Wait for USB to become ready

month_name = ["", "January", "February", "March", "April",
              "May", "June", "July","Augest", "September",
              "October", "November", "December"]

led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()

timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
print("Clock running!")

# == Important code below! ==

# As far as I understand the pi should get accurate
# time from a time server, from which it will set it
# but for in the simulator I'll comment it out
# ds1307.datetime = gmtime(time())


# Start reading from RTC clock
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=800000)
ds1307 = DS1307(addr=0x68, i2c=i2c)

# convert 24-hr clock to 12-hr clock cause
# i can't real 24-hr time and im not starting now!
if ds1307.hour > 12:
  hour = ds1307.hour - 12
  period = "PM"
else:
  hour = ds1307.hour
  period = "AM"

# get the current RTC time
# print("Current RTC time: {}".format(ds1307.datetime))

print("Date: {} {:02d}, {:04d}".format(
  month_name[ds1307.month],
  ds1307.day,
  ds1307.year
))

print("Time: {:02d}:{:02d} {}".format(
  hour,
  ds1307.minute,
  period
))
