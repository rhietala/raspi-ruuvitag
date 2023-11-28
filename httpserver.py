"""
Simple http server, that returns data in json.
Executes get data for sensors in the background.

Follows
https://github.com/ttu/ruuvitag-sensor/blob/master/examples/http_server_asyncio_rx.py
"""

import json
import logging
from datetime import datetime
from inspect import currentframe, getframeinfo
from os.path import abspath, dirname
from typing import Dict, Tuple, TypedDict

from aiohttp import web
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive  # type: ignore


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

# mutable state for current ruuvitag data
STATE: Dict[Mac, RuuviData] = {}


async def get_all_data(_):
    """Return all data"""
    return web.json_response(STATE)


async def get_data(request):
    """Return data for a specific tag"""
    mac: Mac = request.match_info.get("mac")
    if mac not in STATE:
        return web.json_response(status=404)

    # check if data is older than 1 hour
    updated_at = datetime.fromisoformat(STATE[mac]["time"])
    if (datetime.utcnow() - updated_at).total_seconds() > 3600:
        STATE.pop(mac)
        return web.json_response(status=404)

    return web.json_response(STATE[mac])


def setup_routes(app):
    """Setup routes for the web application"""
    app.router.add_get("/", get_all_data)
    app.router.add_get("/{mac}", get_data)


def update_state(data: Tuple[Mac, RuuviData]):
    """Update http server state with new data"""
    mac, ruuvi_data = data
    STATE[mac] = ruuvi_data


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)

    path = dirname(abspath(getframeinfo(currentframe()).filename))
    with open(f"{path}/ruuvitags.json", "r", encoding="utf-8") as file:
        tags = json.load(file)

    logging.info("Read %i tags from ruuvitags.json", len(tags))

    data_stream = RuuviTagReactive(tags).get_subject()
    data_stream.subscribe(update_state)

    logging.info("Started listening to ruuvitags")

    app = web.Application()
    setup_routes(app)
    web.run_app(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
