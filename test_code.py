from machine import Pin
import utime

rows = [Pin(9), Pin(8), Pin(7), Pin(6)]
cols = [Pin(5), Pin(4), Pin(3), Pin(2)]

row_pins = [Pin(pin_num, Pin.OUT) for pin_num in rows]
col_pins = [Pin(pin_num, Pin.IN, Pin.PULL_DOWN) for pin_num in cols]

keypad = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def keypad_irq_handler(col_pin):
    print("irq triggered")

    for row_index, row_pin in enumerate(row_pins):
        row_pin.low()
        if not col_pin.value(): # If column turns off with the row, we found it!
            key_pressed = keypad[row_index][col_pins.index(col_pin)]
            print(key_pressed)

    for row in rows:
        row.high()
    utime.sleep(0.1)


# Set up row pins and power them
for row in rows:
    row.high()
    print(f"registered {row}={row.value()}")

# Set up column pins and interrupts
for col in cols:
    print(f"registered {col}")
    col.irq(trigger=Pin.IRQ_RISING, handler=keypad_irq_handler)

while True:
    utime.sleep(0.2)
