import time

import _thread
from machine import I2C, Pin, Timer, PWM

from timing import timeit

# Drivers for the RTC and the display!
# Credit: https://github.com/mcauser/micropython-tinyrtc-i2c
from ds1307 import DS1307

# Credit: https://github.com/T-622/RPI-PICO-I2C-LCD
from pico_i2c_lcd import I2cLcd

#import weather

time.sleep(0.1) # Wait for USB to become ready

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

# Define custom characters
lcd.custom_char(1, bytearray([0x0E,0x0A,0x0E,0x00,
0x00,0x00,0x00,0x00]))


# As far as I understand the pi should get accurate
# time from a time server, from which it will set it

# Convert to different times for testing lol
#pi_time = list(time.gmtime(time.time()))  # convert to list for editing
#pi_time[3] = 10
#pi_time[4] = 59
#pi_time[5] = 50
#ds1307.datetime = tuple(pi_time) # It expects a tuple type lol


# Setup buttons, buzzer and variables for the alarm
alarm_buzzer = PWM(Pin(20))
alarm_buzzer.freq(1000)
alarm_toggle = False # Determines whether to toggle the sound
alarm_status = False # Determines whether alarm is on

alarm = Timer()

alarm_btn = Pin(21, Pin.IN, Pin.PULL_UP)
hour_btn = Pin(26, Pin.IN, Pin.PULL_UP)
minute_btn = Pin(27, Pin.IN, Pin.PULL_UP)

alarm_last = time.ticks_ms()
hour_last = time.ticks_ms()
minute_last = time.ticks_ms()

alarm_config_mode = False

alarm_time = None

# Pause loops when this is `True`
halt_loop = False


# Bugfix: Don't print text to screen when clock is halted
def screentext(string: str):
    if not halt_loop:
        print(f"adding text: {string}")
        lcd.putstr(string)

def toggle_alarm(timer):
    global alarm_toggle
    print(alarm_toggle)
    if alarm_toggle:
        alarm_buzzer.duty_u16(500)
    else:
        alarm_buzzer.duty_u16(0)
    alarm_toggle = not alarm_toggle


def button_handler(pin):
    global alarm_last, hour_last, minute_last
    global halt_loop, alarm_config_mode, alarm_time

    if pin is alarm_btn:
        if time.ticks_diff(time.ticks_ms(), alarm_last) > 300:
            alarm_last = time.ticks_ms()
            if not alarm_config_mode:
                alarm_config_mode = True
                halt_loop = True

                dt_obj = ds1307.datetime
                if not alarm_time:
                    alarm_time = {
                        "hour": int(get_hour(dt_obj, get_period=False)),
                        "minute": int(dt_obj[4]),
                        "period": get_hour(dt_obj, get_period=True)
                    }

                lcd.clear()

                lcd.putstr("Set alarm:")
                lcd.move_to(0,1)

                lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")
                print('Boop, setup alarm!')
            else:
                alarm_config_mode = False
                halt_loop = False
                lcd.clear()
                print("setup alarm done")
    
    elif pin is hour_btn:
        if time.ticks_diff(time.ticks_ms(), hour_last) > 100:
            if alarm_config_mode:
                hour_last = time.ticks_ms()
                if alarm_time["hour"] == 12:
                    alarm_time["hour"] = 1
                    alarm_time["period"] = "AM" if alarm_time["period"] == "PM" else "PM"
                else:
                    alarm_time["hour"] += 1
                lcd.move_to(0,1)
                lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")
    
    elif pin is minute_btn:
        if time.ticks_diff(time.ticks_ms(), minute_last) > 100:
            if alarm_config_mode:
                minute_last = time.ticks_ms()
                if alarm_time["minute"] == 59:
                    alarm_time["minute"] = 0
                    if alarm_time["hour"] == 12:
                        alarm_time["hour"] = 1
                        alarm_time["period"] = "AM" if alarm_time["period"] == "PM" else "PM"
                    else:
                        alarm_time["hour"] += 1
                else:
                    alarm_time["minute"] += 1
                lcd.move_to(0,1)
                lcd.putstr(f"{alarm_time['hour']:02d}:{alarm_time['minute']:02d} {alarm_time['period']}")


alarm_btn.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
hour_btn.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
minute_btn.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)


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


while True:
    previous_second = ds1307.second

    lcd.clear()
    dt_obj = ds1307.datetime

    lcd.move_to(0,0)
    screentext(get_date(dt_obj))

    lcd.move_to(0,1)
    screentext(f"{get_hour(dt_obj, get_period=False)}:{dt_obj[4]:02d}:{dt_obj[5]:02d} {get_hour(dt_obj, get_period=True)}")

    while ds1307.second % 10 != 0 or ds1307.second == previous_second:
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
        previous_second = dt_obj[5]

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
                            alarm.init(mode=Timer.PERIODIC, period=1500, callback=toggle_alarm)
        
        time.sleep(0.2)


    lcd.clear()

    lcd.move_to(0,0)
    screentext(f"32{chr(1)}c  50%")
    lcd.move_to(0,1)
    screentext("Partly Cloudly")

    previous_second = ds1307.second

    while ds1307.second % 10 != 0 or ds1307.second == previous_second:
        dt_obj = ds1307.datetime
        if alarm_time is not None and not alarm_status:
            if f"{alarm_time['hour']:02d}" == get_hour(dt_obj):
                if alarm_time["minute"] == dt_obj[4]: 
                    if alarm_time["period"] == get_hour(dt_obj, get_period=True):
                            alarm_status = True
                            alarm.init(mode=Timer.PERIODIC, period=1500, callback=toggle_alarm)

        loop_ran = False
        while halt_loop: # Halt loop when paused
            time.sleep(0.1)
            loop_ran = True

        if loop_ran: # Reprint weather IF it was stopped by menu
            lcd.move_to(0,0)
            screentext(f"32{chr(1)}c  50%")
            lcd.move_to(0,1)
            screentext("Partly Cloudly")

        time.sleep(0.2)
