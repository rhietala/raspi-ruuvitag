"""
Simple script to scan for RuuviTags and print their data.

Follows examples from https://pypi.org/project/ruuvitag-sensor/
"""

from ruuvitag_sensor.ruuvi import RuuviTagSensor  # type: ignore
from ruuvitag_sensor.log import log  # type: ignore

log.enable_console()

RuuviTagSensor.find_ruuvitags()
