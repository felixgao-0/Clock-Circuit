from time import sleep

from machine import Pin, Timer
import utime



sleep(0.1) # Wait for USB to become ready

led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()

timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
print("Clock on!")

# == Important code below ==
sensor_temp = machine.ADC(machine.ADC.CORE_TEMP)
conversion_factor = 3.3 / (65535)

rtc=machine.RTC()
last_reading = None

while True:
    reading = sensor_temp.read_u16() * conversion_factor
    timestamp=rtc.datetime()
    temperature = 27 - (reading - 0.706)/0.001721

    timestring="%04d-%02d-%02d %02d:%02d"%(timestamp[0:3] +timestamp[4:6])

    if last_reading != timestring:
      print(timestring)
      last_reading=timestring

    utime.sleep(1)
