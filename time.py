from datetime import datetime
from Adafruit_LED_Backpack import SevenSegment

DISPLAY_ADDRESS = 0x70

display = SevenSegment.SevenSegment(address=DISPLAY_ADDRESS, busnum=1)
display.begin()
display.print_number_str(datetime.now().strftime('%H%M'))
display.set_colon(True)
display.write_display()
