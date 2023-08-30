#!/usr/bin/env python3
"""
Ruuvitag and MPD display for Raspberry Pi with three Adafruit 7-segment displays.

This is similar to thermometer_display.py, but it can be used without
Home Assistant, and it displays the elapsed time of the currently playing song in MPD.
"""
import logging
import subprocess
from datetime import datetime
from time import sleep
from typing import Any, Optional, Sequence, TypedDict, Tuple, Dict

from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive  # type: ignore

# pylint: disable=import-error
from Adafruit_LED_Backpack import SevenSegment  # type: ignore

LED_BRIGHTNESS_HIGH = 15
LED_BRIGHTNESS_LOW = 1

# shorter update interval will use more CPU and have smoother transitions
# this is visible especially with the elapsed time display
UPDATE_INTERVAL = 0.1  # seconds

RUUVITAGS = ["FB:4C:74:E5:DC:BD"]


class RuuviData(TypedDict):
    """RuuviTag data"""

    data_format: int
    humidity: float
    temperature: float
    pressure: float
    acceleration: float
    acceleration_x: int
    acceleration_y: int
    acceleration_z: int
    tx_power: int
    battery: int
    movement_counter: int
    measurement_sequence_number: int
    mac: str
    time: str


Mac = str


class State(TypedDict):
    """State to display."""

    ruuvitags: Dict[Mac, RuuviData]
    time: Optional[str]
    temperature: Optional[float]
    elapsed: Optional[str]


STATE: State = {
    "ruuvitags": {},
    "time": None,
    "temperature": None,
    "elapsed": None,
}


def display_time(display) -> None:
    """Display the current time on the 7-segment display."""

    current_time = datetime.now().strftime("%H%M")
    if current_time != STATE["time"]:
        STATE["time"] = current_time
        display.clear()
        if STATE["time"] is not None:
            display.print_number_str(STATE["time"])
            display.set_colon(True)
        else:
            display.print_number_str("----")
        display.write_display()


def display_ruuvitag(display: Any, mac: Mac) -> None:
    """Display the temperatures on the 7-segment displays."""

    current_temperature = None
    if mac in STATE["ruuvitags"]:
        current_temperature = STATE["ruuvitags"][mac]["temperature"]

    if current_temperature != STATE["temperature"]:
        STATE["temperature"] = current_temperature

        display.clear()
        if STATE["temperature"] is not None:
            display.print_float(STATE["temperature"], decimal_digits=1)
        else:
            display.print_number_str("----")

        display.write_display()


def display_elapsed_time(display: Any) -> None:
    """
    Display the elapsed time of the currently playing song in MPD.

    Example output is:

    $ mpc status
    Kate Bush - The Big Sky (Meteorogical mix)
    [paused]  #23/28   7:30/7:44 (96%)
    volume: 15%   repeat: off   random: off   single: off   consume: off

    Extract "7:30" from the second line and print as "0730" with
    a colon between the digits.
    """

    try:
        mpc_status = subprocess.run(["mpc", "status"], capture_output=True)
        elapsed = (
            mpc_status.stdout.decode("utf-8")
            .split("\n")[1]
            .split()[2]
            .split("/")[0]
            .split(":")
        )
        current_elapsed = f"{elapsed[0]}{elapsed[1]}"
    except Exception:
        current_elapsed = None

    if current_elapsed != STATE["elapsed"]:
        STATE["elapsed"] = current_elapsed

        display.clear()

        if STATE["elapsed"] is not None:
            display.print_number_str(STATE["elapsed"])
            display.set_colon(True)
        else:
            display.print_number_str("----")

        display.write_display()


def set_display_brightness(displays: Sequence[Any]) -> None:
    """Set the brightness of the displays based on the time of day."""
    brightness = (
        LED_BRIGHTNESS_HIGH
        if 8 <= datetime.now().hour < 21
        else LED_BRIGHTNESS_LOW
    )
    for display in displays:
        display.set_brightness(brightness)


def update_state(data: Tuple[Mac, RuuviData]):
    """Update http server state with new data"""
    mac, ruuvi_data = data
    STATE["ruuvitags"][mac] = ruuvi_data


def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    logging.info("Initializing displays")

    displays = (
        SevenSegment.SevenSegment(address=0x70, busnum=1),
        SevenSegment.SevenSegment(address=0x74, busnum=1),
        SevenSegment.SevenSegment(address=0x72, busnum=1),
    )

    for display in displays:
        display.begin()
        display.set_brightness(LED_BRIGHTNESS_HIGH)

    logging.info("Initializing RuuviTags")

    data_stream = RuuviTagReactive(RUUVITAGS).get_subject()
    data_stream.subscribe(update_state)

    logging.info("Starting main loop, exit with Ctrl-C")

    while True:
        display_time(displays[0])
        display_ruuvitag(displays[1], RUUVITAGS[0])
        display_elapsed_time(displays[2])

        sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
