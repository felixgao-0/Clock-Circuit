import time

import dht
from machine import Pin, Timer, ADC


time.sleep(0.1) # Wait for USB to become ready

led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()

timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
print("Clock on!")


#Pin modes here
temp = dht.DHT22(machine.Pin(18))


while True:
  print(temp.temperature())    
  time.sleep(0.1)
