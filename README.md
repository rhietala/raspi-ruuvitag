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

Installing dependencies:

```sh
python -m pip install -r requirements.txt
```

Setting up systemd configurations:

```sh

```

## Development

Installing development dependencies:

```sh
python -m pip install -r requirements-dev.txt
```

Linting

```sh
./lint.sh
```

## ruuvitag-find-sensors.py

Simple script to output scanned ruuvitags to console.

## ruuvitag-webserver.py

This is relevant to all raspberries that fetch data from ruuvitags.
