from datetime import datetime
from Adafruit_LED_Backpack import SevenSegment

hour = datetime.now().hour
day = 8 <= hour <= 8
brightness = 15 if day else 2

for address in [0x70, 0x71, 0x72]:
    display = SevenSegment.SevenSegment(address=address, busnum=1)
    display.begin()
    display.set_brightness(1)
    display.print_hex(0xffff)
    display.write_display()
