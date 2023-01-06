# Ruuvitag utilities on Raspberry Pi for HomeAssistant

A collection of my personal scripts for getting data from
[RuuviTag](https://ruuvi.com/) sensors to
[HomeAssistant](https://www.home-assistant.io/) through
[Raspberry Pi](https://www.raspberrypi.org/) (zeros).

## Architecture

Data fetching

```
ruuvitag --- raspberry pi --- homeassistant

      bluetooth          http
```

The idea is that Raspberry Pi scans for ruuvitags and shares their live data with
a simple http api. HomeAssistant fetches data through http, stores the history
and presents it.

## Prerequisites on Raspberries

Devops is not automated, these have to be done manually.

Installation:

```sh
$ pwd
/home/pi

$ sudo apt-get install bluez bluez-hcidump git
$ git clone https://github.com/rhietala/raspi-ruuvitag.git
$ cd raspi-ruuvitag
$ python -m pip install -r requirements.txt
```

## find_ruuvitags.py

Simple script to output scanned ruuvitags to console.

This can be used to find the MAC addresses of ruuvitags, and check which raspberry
has connectivity to which ruuvitags. This is important to know so that HomeAssistant
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

Simple HTTP server that serves data from ruuvitags as JSON.

Ruuvitag MAC addresses have to be manually configured in `ruuvitags.json`.

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

## Development

Installing development dependencies:

```sh
$ python -m pip install -r requirements-dev.txt
```

Linting

```sh
$ ./lint.sh
```
