from w1thermsensor import W1ThermSensor
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

measurements = []

for sensor in W1ThermSensor.get_available_sensors():
    temp = sensor.get_temperature()
    if temp < 80: # 85 is an errorcode
        tags = sensor_tags.get(sensor.id, {})
        tags["sensor_id"] = sensor.id
        tags["host"] = platform.node()
        measurements.append({
            "measurement": "temperature",
            "time": datetime.datetime.utcnow().isoformat() + 'Z',
            "tags": tags,
            "fields": {
                "value": temp
            }
        })

print json.dumps(measurements, indent=4, sort_keys=True)
if measurements: dbclient.write_points(measurements)
