from Adafruit_LED_Backpack import SevenSegment
from datetime import datetime
from requests import get


API_ENDPOINT = "http://192.168.1.2:8123/api/states/"
HEADERS = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIwNDEwMWJiMGIyYzM0NTgzYTg4NGE0YTdlNGU1OGM3YiIsImlhdCI6MTY2MDM3MzU0NywiZXhwIjoxOTc1NzMzNTQ3fQ.HFD9Gxa3Hnf4w8-pxpAQdEt5vlww5u3ETEG0nXtnopA",
    "content-type": "application/json",
}

brightness = 15 if (8 <= datetime.now().hour <= 8) else 1

for [display_address, sensor_id] in [
    [0x71, "sensor.a11b_temperature"],
    [0x72, "sensor.ulkolampotila"],
]:
    response = get(API_ENDPOINT + sensor_id, headers=HEADERS)
    response.raise_for_status()

    display = SevenSegment.SevenSegment(address=display_address, busnum=1)
    temp = float(response.json()["state"])

    display.begin()
    display.print_float(temp, decimal_digits=1, justify_right=True)
    display.set_brightness(brightness)
    display.write_display()
