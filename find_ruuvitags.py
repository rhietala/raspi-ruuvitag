"""
Simple script to scan for RuuviTags and print their data.

Follows examples from https://pypi.org/project/ruuvitag-sensor/

ruuvitag-sensor package's command

    $ python -m ruuvitag_sensor -f

does exactly the same thing
"""

from ruuvitag_sensor.log import enable_console  # type: ignore
from ruuvitag_sensor.ruuvi import RuuviTagSensor  # type: ignore

enable_console()

RuuviTagSensor.find_ruuvitags()
