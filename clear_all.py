from datetime import datetime
from Adafruit_LED_Backpack import SevenSegment

for address in [0x70, 0x71, 0x72]:
    display = SevenSegment.SevenSegment(address=address, busnum=1)
    display.begin()
    display.set_led(0, False)
    display.set_led(1, False)
    display.set_led(2, False)
    display.set_led(3, False)
    display.set_colon(False)
    display.write_display()
