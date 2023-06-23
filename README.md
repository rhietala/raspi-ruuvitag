# Ruuvitag utilities on Raspberry Pi for HomeAssistant

A collection of my personal scripts for getting data from
[RuuviTag](https://ruuvi.com/) sensors to
[HomeAssistant](https://www.home-assistant.io/) through
[Raspberry Pi](https://www.raspberrypi.org/) (zeros).

## Architecture

Data fetching

```
RuuviTag --- Raspberry Pi --- HomeAssistant

      Bluetooth          HTTP
```

The idea is that Raspberry Pi scans for ruuvitags and shares their live data with
a simple http api. HomeAssistant fetches data through HTTP, stores the history
and presents it.

Thermometer display fetches data from HomeAssistant over HTTP and shows it.

Instructions for building the case are in separate file
[thermometer-display.md](thermometer-display.md)

![Photo of thermometer display in action](img/IMG_2431.jpeg)

## Prerequisites on Raspberries

Devops is not automated, these have to be done manually.

Raspberry Pi boot configuration, `/boot/config.txt` must have these lines:

```
[all]
dtparam=i2c1=on
dtparam=i2c_arm=on
dtoverlay=hifiberry-dac
```

Installation:

```sh
$ pwd
/home/pi

$ sudo usermod -a -G i2c pi
$ sudo apt-get install bluez bluez-hcidump git
$ sudo update-alternatives --install  /usr/bin/python python /usr/bin/python3 1
$ sudo timedatectl set-timezone Europe/Helsinki
$ git clone https://github.com/rhietala/raspi-ruuvitag.git
$ cd raspi-ruuvitag
$ python -m pip install -r requirements.txt
```

## find_ruuvitags.py

Simple script to output scanned RuuviTags to console.

This can be used to find the MAC addresses of ruuvitags, and check which Raspberry Pi
has connectivity to which RuuviTags. This is important to know so that HomeAssistant
can be configured correctly.

```sh
$ python find_ruuvitags.py

Finding RuuviTags. Stop with Ctrl+C.
Start receiving broadcasts (device hci0)
FYI: Calling a process with sudo: hciconfig hci0 reset
FYI: Spawning process with sudo: hcitool -i hci0 lescan2 --duplicates --passive
FYI: Spawning process with sudo: hcidump -i hci0 --raw
D7:98:F9:48:88:7A
{'data_format': 5, 'humidity': 40.05, 'temperature': 18.94, 'pressure': 1013.12, 'acceleration': 1053.9525606022312, 'acceleration_x': 880, 'acceleration_y': -580, 'acceleration_z': -4, 'tx_power': 4, 'battery': 2844, 'movement_counter': 27, 'measurement_sequence_number': 48598, 'mac': 'd798f948887a'}
C7:3C:89:4D:AF:53
{'data_format': 5, 'humidity': 37.79, 'temperature': 19.0, 'pressure': 1013.73, 'acceleration': 1032.4495145042201, 'acceleration_x': 1032, 'acceleration_y': 28, 'acceleration_z': -12, 'tx_power': 4, 'battery': 2904, 'movement_counter': 53, 'measurement_sequence_number': 48333, 'mac': 'c73c894daf53'}
DC:AA:61:EC:A9:5B
{'data_format': 5, 'humidity': 83.64, 'temperature': -8.22, 'pressure': 1014.29, 'acceleration': 1057.4686756590004, 'acceleration_x': 1036, 'acceleration_y': -212, 'acceleration_z': 0, 'tx_power': 4, 'battery': 2577, 'movement_counter': 221, 'measurement_sequence_number': 47305, 'mac': 'dcaa61eca95b'}
```

The output is exactly the same as with ruuvitag-sensor package's command

```sh
$ python -m ruuvitag_sensor -f
```

## httpserver.py

Simple HTTP server that serves data from RuuviTags as JSON.

RuuviTag MAC addresses have to be manually configured in `ruuvitags.json`.

It has two routes:

- `/` returns latest data from all scanned ruuvitags
- `/<mac>` returns latest data for a given ruuvitag

Setting up systemd:

```sh
$ sudo ln -s /home/pi/raspi-ruuvitag/ruuvitag-httpserver.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable ruuvitag-httpserver
$ sudo systemctl start ruuvitag-httpserver
$ sudo systemctl status ruuvitag-httpserver

● ruuvitag-httpserver.service - Ruuvitag sensor readings
     Loaded: loaded (/home/pi/raspi-ruuvitag/ruuvitag-httpserver.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2023-01-06 15:33:35 EET; 1min 51s ago
   Main PID: 20924 (python)
      Tasks: 17 (limit: 876)
        CPU: 24.867s
     CGroup: /system.slice/ruuvitag-httpserver.service
             ├─20924 python httpserver.py
             ├─20928 python httpserver.py
             ├─20939 python httpserver.py
             ├─20946 python httpserver.py
             ├─20958 /usr/bin/sudo hcitool -i hci0 lescan2 --duplicates --passive
             ├─20959 /usr/bin/sudo hcidump -i hci0 --raw
             ├─20960 hcitool -i hci0 lescan2 --duplicates --passive
             └─20961 hcidump -i hci0 --raw
```

The systemd service assumes that this repository is cloned to directory
`/home/pi/raspi-ruuvitag`, and that user and group are `pi` / `pi`.

After this, curl should return something:

```sh
$ curl http://192.168.1.117:5000/ | jq | head

{
  "CC:92:E5:0C:A1:1B": {
    "data_format": 5,
    "humidity": 37.8,
    "temperature": 17.21,
    "pressure": 1013.11,
    "acceleration": 996.0803180466925,
    "acceleration_x": -852,
    "acceleration_y": 516,
    "acceleration_z": 4,
```

HomeAssistant configuration should be something like this (`configuration.yaml`):

```yaml
sensor:
  - platform: "command_line"
    unique_id: "CC:92:E5:0C:A1:1B.temp"
    name: "Olohuone lämpötila"
    command: "curl 'http://192.168.1.241:5000/CC:92:E5:0C:A1:1B'"
    unit_of_measurement: "°C"
    value_template: "{{ value_json.temperature }}"
```

## thermometer_display.py

Thermometer display for Raspberry Pi with three Adafruit 7-segment displays.

This is highly specific to my setup, but it should be easy to adapt to your
needs. It displays the current time on the first display and two temperatures
on the other two displays. The temperatures are read from a Home Assistant
instance using the Home Assistant API.

[Adafruit LED Backpack](https://github.com/adafruit/Adafruit_Python_LED_Backpack)
Python library must be configured in the Raspberry with displays.

API token must be created in HomeAssistant through User Profile - Long-Lived
Access Tokens, and it must be stored in `thermometer-display.service` to
`HOMEASSISTANT_BEARER_TOKEN`.

Setting up systemd:

```sh
$ sudo ln -s /home/pi/raspi-ruuvitag/thermometer-display.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable thermometer-display
$ sudo systemctl start thermometer-display
$ sudo systemctl status thermometer-display

● thermometer-display.service - Thermometer display
     Loaded: loaded (/home/pi/raspi-ruuvitag/thermometer-display.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2023-01-07 20:58:20 EET; 10min ago
   Main PID: 1249 (python)
      Tasks: 1 (limit: 876)
        CPU: 16.327s
     CGroup: /system.slice/thermometer-display.service
             └─1249 python thermometer_display.py

Jan 07 21:08:25 rpi env[1249]: INFO:root:Got reading: 16.95 for sensor sensor.a11b_temperature
```

## Development

Installing development dependencies:

```sh
$ python -m pip install -r requirements-dev.txt
```

Linting

```sh
$ ./lint.sh
```
