"""
Thermometer display for Raspberry Pi with three Adafruit 7-segment displays.

This is highly specific to my setup, but it should be easy to adapt to your
needs. It displays the current time on the first display and two temperatures
on the other two displays. The temperatures are read from a Home Assistant
instance using the Home Assistant API.
"""
import logging
import os
from datetime import datetime
from time import sleep
from typing import Any, List, Optional, TypedDict

import requests

# pylint: disable=import-error
from Adafruit_LED_Backpack import SevenSegment  # type: ignore

UPDATE_INTERVAL = 5  # seconds
HOMEASSISTANT_UPDATE_CYCLE = (
    12  # UPDATE_INTERVAL * HOMEASSISTANT_UPDATE_CYCLE = 60 seconds
)
HOMEASSISTANT_ENDPOINT = "http://192.168.1.2:8123/api/states"
HOMEASSISTANT_SENSORS = [
    "sensor.makuuhuone_lampotila",
    "sensor.ulkolampotila",
]
LED_BRIGHTNESS_HIGH = 15
LED_BRIGHTNESS_LOW = 1

Display = Any


class State(TypedDict):
    """State for thermometer."""

    brightness: int
    time: Optional[str]
    temperatures: List[Optional[float]]
    homeassistant_update_cycle: int


STATE: State = {
    "brightness": LED_BRIGHTNESS_HIGH,
    "time": None,
    "temperatures": [None, None],
    "homeassistant_update_cycle": 0,  # update on first iteration
}


def display_time(display: Display) -> None:
    """Display the current time on the 7-segment display."""
    current_time = datetime.now().strftime("%H%M")

    if current_time != STATE["time"]:
        STATE["time"] = current_time
        display.clear()
        display.print_number_str(STATE["time"])
        display.set_colon(True)
        display.write_display()


def display_temperatures(
    displays: List[Display], temperatures: List[Optional[float]]
) -> None:
    """Display the temperatures on the 7-segment displays."""
    for i, (display, temp, prev_temp) in enumerate(
        zip(displays, temperatures, STATE["temperatures"])
    ):
        if temp != prev_temp:
            STATE["temperatures"][i] = temp
            display.clear()
            if temp:
                display.print_float(temp, decimal_digits=1)
            else:
                display.print_number_str("----")

            display.write_display()


def set_display_brightness(displays: List[Display]) -> None:
    """Set the brightness of the displays based on the time of day."""
    brightness = (
        LED_BRIGHTNESS_HIGH
        if 8 <= datetime.now().hour < 21
        else LED_BRIGHTNESS_LOW
    )
    if brightness != STATE["brightness"]:
        for display in displays:
            display.set_brightness(brightness)


def get_sensor_reading(sensor: str, bearer_token: str) -> Optional[float]:
    """Get a sensor reading from the Home Assistant API."""
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "content-type": "application/json",
    }

    try:
        response = requests.get(
            f"{HOMEASSISTANT_ENDPOINT}/{sensor}", headers=headers, timeout=5
        )
    except requests.exceptions.ConnectionError as error:
        logging.error("Error while getting sensor reading: %s", error)
        return None

    if not response:
        logging.warning("Failed to get reading for sensor %s", sensor)
        return None

    try:
        sensor_state = response.json()["state"]
        value = float(sensor_state)
    except ValueError:
        logging.warning("Got non-float value %s for sensor %s", sensor_state, sensor)
        return None

    if value > 1000:
        logging.warning(
            "Got value %s > 1000 for sensor %s, ignoring", value, sensor
        )
        return None

    return value


def get_temperature_readings(bearer_token: str) -> List[Optional[float]]:
    """Get temperature readings from the Home Assistant API."""
    readings = (
        get_sensor_reading(sensor, bearer_token)
        for sensor in HOMEASSISTANT_SENSORS
    )

    return [
        float(reading) if reading is not None else None for reading in readings
    ]


def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    bearer_token = os.getenv("HOMEASSISTANT_BEARER_TOKEN")
    assert (
        bearer_token is not None
    ), "HOMEASSISTANT_BEARER_TOKEN environment variable not set"

    logging.info("Initializing displays")

    displays = (
        SevenSegment.SevenSegment(address=0x70, busnum=1),
        SevenSegment.SevenSegment(address=0x74, busnum=1),
        SevenSegment.SevenSegment(address=0x72, busnum=1),
    )

    for display in displays:
        display.begin()
        display.set_brightness(STATE["brightness"])
        display.print_number_str("----")
        display.write_display()

    logging.info("Starting main loop, exit with Ctrl-C")

    while True:
        if STATE["homeassistant_update_cycle"] <= 0:
            temperatures = get_temperature_readings(bearer_token)
            display_temperatures(
                displays[1:], temperatures
            )
            STATE["homeassistant_update_cycle"] = HOMEASSISTANT_UPDATE_CYCLE
        else:
            STATE["homeassistant_update_cycle"] -= 1

        set_display_brightness(displays)
        display_time(displays[0])
        sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
