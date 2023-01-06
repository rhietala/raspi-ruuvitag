from ruuvitag_sensor.ruuvi import RuuviTagSensor
from influxdb import InfluxDBClient
import datetime
import platform
import json

dbclient = InfluxDBClient(
    host="hietala.org",
    username="pi",
    password="pi",
    port=8086,
    database="temperature"
)

with open('sensors.json') as f:
    sensor_tags = json.load(f)

all_data = RuuviTagSensor.get_data_for_sensors()
time = datetime.datetime.utcnow().isoformat() + 'Z'
measurements = []

for sensor_id, data in all_data.items():
    tags = sensor_tags.get(sensor_id, {})
    tags["sensor_id"] = sensor_id
    tags["host"] = platform.node()
    measurements.append({
        "measurement": "ruuvitag",
        "time": time,
        "tags": tags,
        "fields": data
    })

print json.dumps(measurements, indent=4, sort_keys=True)
if measurements:
    dbclient.write_points(measurements)
