[![ci badge](https://github.com/rmfukuda/sensor-poc/actions/workflows/ci.yml/badge.svg)](https://github.com/rmfukuda/sensor-poc/actions/workflows/ci.yml)

# Description
This repository serves as a proof-of-concept (POC) for an application that involves data acquisition and visualization of sensor measurements.


## Features:
- Firmware for the ESP32 device that includes BLE functionality using the ESP-IDF framework.
- Software written in Python for receiving data from the ESP32 device over BLE.
- Full application including the following steps: sensor data collection, BLE transmission, SQL database storage and data visualization.


# Instructions
Required hardware:
- ESP32-S3-DevKitC-1 development kit
- Notebook with BLE

1. Go to the software directory and install the python dependencies inside a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Turn on the ESP32 and activate the notebook's BLE

3. Run the python script with
```
python3 main.py
```

The interactive plot can be visualized inside a web browser:
![python interactive plot](img/interactive_plot.gif)


# Implementation details
- Testing and Docker: unit tests are configured and executed inside Docker. It allows us to run the automated tests on cloud, for example, during our CI builds.
- Continuous Integration (CI): the configured CI pipeline for automated testing is presented inside `.github/workflows`.
- Dependabot: the bot is configured for automatic python dependency updates. Combined with CI, it reduces the code maintenance time.
- FreeRTOS: the firmware is implemented with FreeRTOS inside two tasks. One task for sensor reading and another task for BLE transmission. The tasks are synchronized using semaphores.
- SQL: the sensor readings are stored inside the SQL database. SQLite was chosen for its simplicity and native python support without third-party libraries.
