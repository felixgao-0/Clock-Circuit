# Alarm Clock

This is a bin submission (or at least a planned bin submission). Thanks Arcade for all the fun I had!

## How to use:

![image](https://github.com/user-attachments/assets/083f3ab1-7e44-461d-82ff-388f7790ca3b)

From left to right are the alarm button, hour button, and minute button. Click the alarm button to set an alarm. You change the time to alarm w/ the hour and minute button. Press the alarm button again to set the alarm. Long press the alarm button to clear the alarm, meaning it will reset and not go off. Long press alarm button when the alarm is active to stop it. Short press to snooze. Accidentally snoozed when you meant to disable it? Just clear the alarm like described before by long pressing the alarm button.

![image](https://github.com/user-attachments/assets/dc05565f-e615-41bf-a2a7-a68d8c0a6d20)

Adjust the photoresistor to simulate darkness. The screen will disable its backlight automatically! It will automatically come on when you press buttons to set alarms, snooze, clear, etc. Press the hour and minute buttons (either one) when the alarm isn't being set to enable the screen backlight at night! 

## AI Usage:
Parts of the code were inspired by prompts with ChatGPT. These were then **_heavily_ modified** to sort my use cases and make the code shorter, more concise, and more accurate. ChatGPT provided the ground work for the long press functions as well as the function `only_ones_changed()`, which identifies if only the ones digit in a second changed, to reduce screenwriting and improve simulation performance. AI is awesome lol. Everything else is written entirely by me with the help of documentation and guides.

## Other Credits:
Thanks to the following git repos for the drivers used!

Real time clock: https://github.com/mcauser/micropython-tinyrtc-i2c

LCD: https://github.com/T-622/RPI-PICO-I2C-LCD
