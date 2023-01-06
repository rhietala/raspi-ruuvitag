from datetime import datetime
from Adafruit_LED_Backpack import SevenSegment

DISPLAY_ADDRESS = 0x70

display = SevenSegment.SevenSegment(address=DISPLAY_ADDRESS, busnum=1)
brightness = 15 if (8 <= datetime.now().hour <= 8) else 1

display.begin()
display.print_number_str(datetime.now().strftime('%H%M'))
display.set_colon(True)
display.set_brightness(brightness)
display.write_display()
