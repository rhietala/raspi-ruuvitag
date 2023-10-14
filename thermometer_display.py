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
from typing import Any, List, Optional, Tuple, TypedDict

import requests

# pylint: disable=import-error
from Adafruit_LED_Backpack import SevenSegment  # type: ignore

UPDATE_INTERVAL = 5  # seconds
HOMEASSISTANT_UPDATE_CYCLE = (
    12  # UPDATE_INTERVAL * HOMEASSISTANT_UPDATE_CYCLE = 60 seconds
)
LED_BRIGHTNESS_HIGH = 15
LED_BRIGHTNESS_LOW = 7

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
            if temp is not None:
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


def get_sensor_reading(
    homeassistant_endpoint: str, sensor: str, bearer_token: str
) -> Optional[float]:
    """Get a sensor reading from the Home Assistant API."""
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "content-type": "application/json",
    }

    try:
        response = requests.get(
            f"{homeassistant_endpoint}/{sensor}", headers=headers, timeout=5
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
        logging.warning(
            "Got non-float value %s for sensor %s", sensor_state, sensor
        )
        return None

    if value > 1000:
        logging.warning(
            "Got value %s > 1000 for sensor %s, ignoring", value, sensor
        )
        return None

    return value


def get_temperature_readings(
    homeassistant_endpoint: str,
    bearer_token: str,
    homeassistant_sensors: List[str],
) -> List[Optional[float]]:
    """Get temperature readings from the Home Assistant API."""
    return [
        get_sensor_reading(homeassistant_endpoint, sensor, bearer_token)
        for sensor in homeassistant_sensors
    ]


def read_env() -> Tuple[List[int], str, str, List[str]]:
    display_addresses_str = os.getenv("DISPLAY_ADDRESSES")
    assert (
        display_addresses_str is not None
    ), "DISPLAY_ADDRESSES environment variable not set"
    display_addresses = [int(s, 0) for s in display_addresses_str.split(";")]
    assert (
        len(display_addresses) == 3
    ), "DISPLAY_ADDRESSES must contain 3 addresses"

    bearer_token = os.getenv("HOMEASSISTANT_BEARER_TOKEN")
    assert (
        bearer_token is not None
    ), "HOMEASSISTANT_BEARER_TOKEN environment variable not set"

    homeassistant_endpoint = os.getenv("HOMEASSISTANT_ENDPOINT")
    assert (
        homeassistant_endpoint is not None
    ), "HOMEASSISTANT_ENDPOINT environment variable not set"

    homeassistant_sensors_str = os.getenv("HOMEASSISTANT_SENSORS")
    assert (
        homeassistant_sensors_str is not None
    ), "HOMEASSISTANT_SENSORS environment variable not set"
    homeassistant_sensors = homeassistant_sensors_str.split(";")
    assert (
        len(homeassistant_sensors) == 2
    ), "HOMEASSISTANT_SENSORS must contain 2 sensors"

    return (
        display_addresses,
        bearer_token,
        homeassistant_endpoint,
        homeassistant_sensors,
    )


def main() -> None:
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    (
        display_addresses,
        bearer_token,
        homeassistant_endpoint,
        homeassistant_sensors,
    ) = read_env()

    logging.info("Initializing displays")

    displays: List[Display] = [
        SevenSegment.SevenSegment(address=address, busnum=1)
        for address in display_addresses
    ]

    for display in displays:
        display.begin()
        display.set_brightness(STATE["brightness"])
        display.print_number_str("----")
        display.write_display()

    logging.info("Starting main loop, exit with Ctrl-C")

    while True:
        if STATE["homeassistant_update_cycle"] <= 0:
            temperatures = get_temperature_readings(
                homeassistant_endpoint, bearer_token, homeassistant_sensors
            )
            display_temperatures(displays[1:], temperatures)
            STATE["homeassistant_update_cycle"] = HOMEASSISTANT_UPDATE_CYCLE
        else:
            STATE["homeassistant_update_cycle"] -= 1

        set_display_brightness(displays)
        display_time(displays[0])
        sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
