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
from typing import Any, Optional, Sequence, TypedDict

import requests

# pylint: disable=import-error
from Adafruit_LED_Backpack import SevenSegment  # type: ignore

UPDATE_INTERVAL = 5
HOMEASSISTANT_ENDPOINT = "http://192.168.1.2:8123/api/states"
HOMEASSISTANT_SENSORS = [
    "sensor.makuuhuone_lampotila",
    "sensor.ulkolampotila",
]
LED_BRIGHTNESS_HIGH = 15
LED_BRIGHTNESS_LOW = 1


class State(TypedDict):
    """State for thermometer."""

    display_colon: bool


STATE: State = {"display_colon": True}


def display_time(display) -> None:
    """Display the current time on the 7-segment display."""
    display.print_number_str(datetime.now().strftime("%H%M"))

    # Colon will change on/off on every update so that
    # it shows whether the display is updating or not
    display.set_colon(STATE["display_colon"])
    STATE["display_colon"] = not STATE["display_colon"]


def display_temperatures(
    displays: Sequence[Any], temperatures: Sequence[Optional[float]]
) -> None:
    """Display the temperatures on the 7-segment displays."""
    for display, temperature in zip(displays, temperatures):
        if temperature:
            display.print_float(temperature, decimal_digits=1)
        else:
            display.print_number_str("----")


def set_display_brightness(displays: Sequence[Any]) -> None:
    """Set the brightness of the displays based on the time of day."""
    brightness = (
        LED_BRIGHTNESS_HIGH
        if 8 <= datetime.now().hour < 21
        else LED_BRIGHTNESS_LOW
    )
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

    if response:
        logging.info(
            "Got reading: %s for sensor %s", response.json()["state"], sensor
        )
        try:
            state = response.json()["state"]
            return float(state)
        except ValueError:
            logging.warning("Got non-float value %s for sensor %s", state, sensor)
            return None

    logging.warning("Failed to get reading for sensor %s", sensor)
    return None


def get_temperature_readings(bearer_token: str) -> Sequence[Optional[float]]:
    """Get temperature readings from the Home Assistant API."""
    readings = [
        get_sensor_reading(sensor, bearer_token)
        for sensor in HOMEASSISTANT_SENSORS
    ]

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
        SevenSegment.SevenSegment(address=0x71, busnum=1),
        SevenSegment.SevenSegment(address=0x72, busnum=1),
    )

    for display in displays:
        display.begin()

    logging.info("Starting main loop, exit with Ctrl-C")

    while True:
        for display in displays:
            display.clear()

        set_display_brightness(displays)
        display_time(displays[0])
        display_temperatures(
            displays[1:], get_temperature_readings(bearer_token)
        )

        for display in displays:
            display.write_display()

        sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
