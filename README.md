# Alarm Clock

This is a [Bin](https://hackclub.com/bin/) submission. Thanks [Arcade](https://hackclub.com/arcade/) for all the fun I had!

**[<<< Find the project here >>>](https://wokwi.com/projects/406608282200416257)**

## How to use:

![image](https://github.com/user-attachments/assets/2e488cbf-cf41-49da-b877-81f12e1105b4)

The keypad controls most of the functions. The functions are as follows:
- A: Configure the alarm time
- B: In alarm config mode, cancel the alarm settings, otherwise clear the alarm so it doesn't go off
- C: Enable the display backlight for 5 seconds when the screen is dimmed (screen dims when dark in the room)
- D: **unused**
- #: Enter key for alarm config mode, save your settings
- *: Change from AM to PM, and vice versa
- 1-9: Add the time in alarm config mode (Numbers are validated so I.e. you can't have 40pm)

---

![image](https://github.com/user-attachments/assets/dc05565f-e615-41bf-a2a7-a68d8c0a6d20)

Adjust the photoresistor to simulate darkness. The screen will disable its backlight automatically! It will automatically come on when you press buttons to set alarms, snooze, clear, etc. Press the hour and minute buttons (either one) when the alarm isn't being set to enable the screen backlight at night! 

---

![image](https://github.com/user-attachments/assets/6ce43ef0-c5c5-4e51-8da1-97cbbd9dd3e3)

The display dims when dark out which I find nice :D. A notification icon will appear (as shown in the image) when an alarm is set. The display shows the current time and date. Time is shown as HH:MM:SS. The date is shown as MM DD, YYYY

---

**[<<< Find the project here >>>](https://wokwi.com/projects/406608282200416257)**

## AI Usage:
Parts of the code were inspired by prompts with ChatGPT. These were then **_heavily_ modified** to sort my use cases and make the code shorter, more concise, and more accurate. ChatGPT provided the ground work for the long press functions as well as the function `only_ones_changed()`, which identifies if only the ones digit in a second changed, to reduce screenwriting and improve simulation performance. AI is awesome lol. Everything else is written entirely by me with the help of documentation and guides.

## Other Credits:
Thanks to the following git repos for the drivers used!

Real time clock: https://github.com/mcauser/micropython-tinyrtc-i2c

LCD: https://github.com/T-622/RPI-PICO-I2C-LCD
