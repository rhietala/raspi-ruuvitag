"""
Simple http server, that returns data in json.
Executes get data for sensors in the background.
Endpoints:
    http://0.0.0.0:5000/data
    http://0.0.0.0:5000/data/{mac}
Requires:
    asyncio - Python 3.5
    aiohttp - pip install aiohttp

https://github.com/ttu/ruuvitag-sensor/blob/master/examples/http_server_asyncio_rx.py
"""

# pylint: disable=duplicate-code

from aiohttp import web
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive

all_data = {}


async def get_all_data(_):
    return web.json_response(all_data)


async def get_data(request):
    mac = request.match_info.get("mac")
    if mac not in all_data:
        return web.json_response(status=404)
    return web.json_response(all_data[mac])


# pylint: disable=redefined-outer-name
def setup_routes(app):
    app.router.add_get("/data", get_all_data)
    app.router.add_get("/data/{mac}", get_data)


if __name__ == "__main__":
    tags = {
        "CC:92:E5:0C:A1:1B": "makuuhuone",
        "D7:98:F9:48:88:7A": "väinön huone",
        "C7:3C:89:4D:AF:53": "olohuone",
        "FB:4C:74:E5:DC:BD": "DCBD",
        "FB:92:57:F0:2C:54": "teiskontie",
        "DC:AA:61:EC:A9:5B": "kaupinkatu",
    }

    def handle_new_data(data):
        global all_data  # pylint: disable=global-variable-not-assigned
        data[1]["name"] = tags[data[0]]
        all_data[data[0]] = data[1]

    ruuvi_rx = RuuviTagReactive(list(tags.keys()))
    data_stream = ruuvi_rx.get_subject()
    data_stream.subscribe(handle_new_data)

    # Setup and start web application
    app = web.Application()
    setup_routes(app)
    web.run_app(app, host="0.0.0.0", port=5000)
