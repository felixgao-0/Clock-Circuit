import time

import _thread
from machine import I2C, Pin, Timer, PWM

from timing import timeit

# Drivers for the RTC and the display!
# Credit: https://github.com/mcauser/micropython-tinyrtc-i2c
from ds1307 import DS1307

# Credit: https://github.com/T-622/RPI-PICO-I2C-LCD
from pico_i2c_lcd import I2cLcd

# Drivers for the keypad
# Credit: https://github.com/PerfecXX/MicroPython-SimpleKeypad
#from keypad import Keypad


time.sleep(0.1) # Wait for USB to become ready


# Setup RTC clock
rtc_clock = I2C(0, scl=Pin(13), sda=Pin(12), freq=800000)
ds1307 = DS1307(addr=0x68, i2c=rtc_clock)

# Setup the display to print everything to!
display = I2C(1, scl=Pin(15), sda=Pin(14), freq=800000)
lcd = I2cLcd(display, 0x27, 2, 16)


# Config & random variables
month_name = ["", "Jan", "Feb", "Mar", "Apr",
              "May", "Jun", "Jul","Aug", "Sept",
              "Oct", "Nov", "Dec"]

# Keypad
row_pins = [Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(7, Pin.OUT), Pin(6, Pin.OUT)]
column_pins = [Pin(5, Pin.IN, Pin.PULL_UP), Pin(4, Pin.IN, Pin.PULL_UP), Pin(3, Pin.IN, Pin.PULL_UP), Pin(2, Pin.IN, Pin.PULL_UP)]

keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

#keypad = Keypad(row_pins, column_pins, keys)

# Setup the dimming system
photo_pin = Pin(16, Pin.IN)
dim_timer = Timer()

# As far as I understand the pi should get accurate
# time from a time server, from which it will set it

# Convert to different times for testing lol
#pi_time = list(time.gmtime(time.time()))  # convert to list for editing
#pi_time[3] = 10
#pi_time[4] = 59
#pi_time[5] = 50
#ds1307.datetime = tuple(pi_time) # It expects a tuple type lol

def keypad_irq_handler(pin):
    print(f"handler run on {pin}")

    for col_pin in column_pins:
        col_pin.value(0)
        for i, row_pin in enumerate(row_pins):
            if not row_pin.value():
                key_pressed = keys[i][column_pins.index(col_pin)]
                col_pin.value(1)
                print(f"key pressed -> {key_pressed}")
        col_pin.value(1)

    time.sleep(0.1) # Debounce

# Set up interrupts for each column pin
for col in column_pins:
    print(f"registered {col}")
    col.irq(trigger=Pin.IRQ_RISING, handler=keypad_irq_handler)

# ^^^ KEYPAD IMPLEMENTATION ^^^


alr_on = False
def screen_light(setting: bool, *, timer: bool = False):
    global alr_on
    if setting:
        if not alr_on:
            alr_on = True
            lcd.backlight_on()

        if timer and photo_pin.value() == 1: # Dim on timer if meant to be dark only
            dim_timer.init(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:screen_light(False))            
    else:
        alr_on = False
        lcd.backlight_off()


def handle_screen(pin):
    if pin.value() == 1:
        screen_light(False)
    elif pin.value() == 0:
        screen_light(True)

photo_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_screen)


# Setup buttons, buzzer and variables for the alarm
alarm_buzzer = PWM(Pin(18))
alarm_buzzer.freq(1000)
alarm_toggle = False # Determines whether to toggle the sound
alarm_status = False # Determines whether alarm is on

alarm = Timer()
clear_display = Timer()

# Buttons
alarm_btn = Pin(21, Pin.IN, Pin.PULL_UP)
hour_btn = Pin(26, Pin.IN, Pin.PULL_UP)
minute_btn = Pin(27, Pin.IN, Pin.PULL_UP)

# Last press time for debounce
alarm_last = time.ticks_ms()
hour_last = time.ticks_ms()
minute_last = time.ticks_ms()

button_pressed = False     # If alarm btn is being pressed
press_duration = 0         # How long the alarm btn was pressed for

alarm_config_mode = False  # Weather the alarm is in setup mode (I.e setting time)
alarm_time = None          # Stores the time the alarm should activate
halt_loop = False          # Pause loop when this is `True`

"""
def close_menu(pin):
    global halt_loop
    lcd.clear()
    halt_loop = False
 
def button_irq_handler(pin):
    global button_pressed, press_duration, halt_loop
    global alarm_status, alarm_time, alarm_last, alarm_config_mode
    
    current_time = time.ticks_ms()
    
    # Debounce
    if time.ticks_diff(current_time, alarm_last) < 50:
        return

    if pin.value() == 0 and not button_pressed: # When pressed
        button_pressed = True
        press_duration = current_time
        alarm_last = current_time  # debounce
    elif pin.value() == 1 and button_pressed:   # When let go
        button_pressed = False
        press_duration = time.ticks_diff(current_time, press_duration)
        alarm_last = current_time  # debounce

        if alarm_status: # Options if the alarm is ON:
            if press_duration > 1000: # Shut off alarm
                alarm_status = False
                time_period = alarm_time["period"]
                alarm_time = None
                alarm.deinit()
                alarm_buzzer.duty_u16(0)

                halt_loop = True
                lcd.clear()
                screen_light(True, timer=True)
                lcd.putstr("Alarm off!")
                lcd.move_to(0,1)
                if time_period == "AM":
                    lcd.putstr("Good morning!")
                else:
                    lcd.putstr("Good afternoon!")

                clear_display.init(mode=Timer.ONE_SHOT, period=1500, callback=close_menu)

            else:
                alarm_time["minute"] += 5 # SNOOZE!

                if alarm_time["minute"] >= 60:
                    alarm_time["hour"] += 1
                    alarm_time["minute"] -= 60
                
                if alarm_time["hour"] > 12:
                    alarm_time["hour"] -= 12
                    alarm_time["period"] = "PM" if alarm_time["period"] == "AM" else "AM"
        
                elif alarm_time["hour"] == 12:
                    alarm_time["period"] = "PM" if alarm_time["period"] == "AM" else "AM"
                
                alarm_status = False
                alarm.deinit()
                alarm_buzzer.duty_u16(0)

                halt_loop = True
                lcd.clear()
                lcd.putstr("Snoozed 5 Min!")
                lcd.move_to(0,1)
                lcd.putstr("Zzzzz...")

                clear_display.init(mode=Timer.ONE_SHOT, period=1500, callback=close_menu)
                screen_light(True, timer=True)

        else: # options if alarm is OFF
            if press_duration > 1000 and alarm_time: # If hold & alarm set, clear alarm
                alarm_time = None
                halt_loop = True
                lcd.clear()
                lcd.putstr("Cleared alarm")

                clear_display.init(mode=Timer.ONE_SHOT, period=1500, callback=close_menu)
                screen_light(True, timer=True)

            elif press_duration < 1000: # Otherwise set or edit alarm, or leave menu
                screen_light(True)

                if not alarm_config_mode:
                    alarm_config_mode = True
                    halt_loop = True

                    dt_obj = ds1307.datetime

                    lcd.clear()
                    if not alarm_time:
                        lcd.putstr("Setup alarm:")
                        alarm_time = {
                            "hour": int(get_hour(dt_obj, get_period=False)),
                            "minute": int(dt_obj[4]),
                            "period": get_hour(dt_obj, get_period=True)
                        }
                    else:
                        lcd.putstr("Edit alarm:")
                    
                    lcd.move_to(0,1)

                    lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")
                else:
                    if photo_pin.value() == 1:
                        screen_light(False)

                    alarm_config_mode = False
                    halt_loop = False
                    lcd.clear()

def hour_handler(pin):
    global hour_last
    global alarm_config_mode, alarm_time

    if time.ticks_diff(time.ticks_ms(), hour_last) < 200: # Debounce
        return
    if alarm_config_mode:
        hour_last = time.ticks_ms()
        if alarm_time["hour"] == 12:
            alarm_time["hour"] = 1
            alarm_time["period"] = "AM" if alarm_time["period"] == "PM" else "PM"
        else:
            alarm_time["hour"] += 1
        lcd.move_to(0,1)
        lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")
    elif pin.value() == 0: # Brighten screen when not alarm mode just cause
        screen_light(True, timer=True)
    

def minute_handler(pin):
    global minute_last
    global alarm_config_mode, alarm_time

    if time.ticks_diff(time.ticks_ms(), minute_last) < 200: # Debounce
        return

    if alarm_config_mode:
        minute_last = time.ticks_ms()
        if alarm_time["minute"] == 59:
            alarm_time["minute"] = 0
        else:
            alarm_time["minute"] += 1
        lcd.move_to(0,1)
        lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")
    elif pin.value() == 0: # Brighten screen when not alarm mode just cause
        screen_light(True, timer=True)


alarm_btn.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_irq_handler)
hour_btn.irq(trigger=Pin.IRQ_RISING, handler=hour_handler)
minute_btn.irq(trigger=Pin.IRQ_RISING, handler=minute_handler)
"""

# Bugfix: Don't print text to screen when clock is halted
def screentext(string: str):
    if not halt_loop:
        lcd.putstr(string)


def toggle_alarm(timer):
    global alarm_toggle
    if alarm_toggle:
        alarm_buzzer.duty_u16(500)
    else:
        alarm_buzzer.duty_u16(0)
    alarm_toggle = not alarm_toggle


def only_ones_changed(prev_time: int, new_time: int):
    if not prev_time: # Handle nonetypes
        return False

    prev_tens_place = prev_time // 10
    prev_ones_place = prev_time % 10
    new_tens_place = new_time // 10
    new_ones_place = new_time % 10

    return prev_tens_place == new_tens_place and prev_ones_place != new_ones_place


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


dt_obj = ds1307.datetime

lcd.move_to(0,0)
screentext(get_date(dt_obj))

lcd.move_to(0,1)
screentext(f"{get_hour(dt_obj, get_period=False)}:{dt_obj[4]:02d}:{dt_obj[5]:02d} {get_hour(dt_obj, get_period=True)}")

previous_second = ds1307.second
while True:
    dt_obj = ds1307.datetime # Save dt object to avoid too many i2c calls
    if (dt_obj[3] == 0) and (dt_obj[4] == 0): # Update date if time is 12:00 am
        lcd.move_to(0,0)
        screentext(get_date(dt_obj))
    

    if dt_obj[4] == 0: # Update hour if minutes at 00
        lcd.move_to(0,1)
        screentext(get_hour(dt_obj, get_period=False))
        lcd.move_to(9,1)
        screentext(get_hour(dt_obj, get_period=True))


    if dt_obj[5] == 0: # Update minute if seconds at 00
        lcd.move_to(3,1)
        screentext(f"{dt_obj[4]:02d}")

    if previous_second != dt_obj[5]: # Only change needed digits
        if only_ones_changed(previous_second, dt_obj[5]):
            lcd.move_to(7,1)
            screentext(str(dt_obj[5] % 10))
        else:
            lcd.move_to(6,1)
            screentext(f"{dt_obj[5]:02d}")
        previous_second = ds1307.second

    loop_ran = False
    while halt_loop: # Halt loop when paused
        time.sleep(0.1)
        loop_ran = True

    if loop_ran:
        dt_obj = ds1307.datetime
        lcd.move_to(0,0)
        screentext(get_date(dt_obj))

        lcd.move_to(0,1)
        screentext(f"{get_hour(dt_obj, get_period=False)}:{dt_obj[4]:02d}:{dt_obj[5]:02d} {get_hour(dt_obj, get_period=True)}")

    if alarm_time is not None and not alarm_status:
        if f"{alarm_time['hour']:02d}" == get_hour(dt_obj):
            if alarm_time["minute"] == dt_obj[4]: 
                if alarm_time["period"] == get_hour(dt_obj, get_period=True):
                    alarm_status = True
                    screen_light(True)
                    alarm.init(mode=Timer.PERIODIC, period=1500, callback=toggle_alarm)
        
    time.sleep(0.2)
