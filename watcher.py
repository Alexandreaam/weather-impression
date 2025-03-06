#!/usr/bin/env python3

import signal
import RPi.GPIO as GPIO
import configparser
import os
import schedule
import time
import gpiod
import gpiodevice
from threading import Thread
from gpiod.line import Bias, Direction, Edge

# config file should be the same folder.
os.chdir('/home/eink/weather-impression')
project_root = os.getcwd()
configFilePath = project_root + '/config.txt'

# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, C and D respectively
LABELS = ['A', 'B', 'C', 'D']

# Create settings for all the input pins, we want them to be inputs
# with a pull-up and a falling edge detection.
INPUT = gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING)

# Find the gpiochip device we need, we'll use
# gpiodevice for this, since it knows the right device
# for its supported platforms.
chip = gpiodevice.find_chip_by_platform()

# Build our config for each pin/line we want to use
OFFSETS = [chip.line_offset_from_id(id) for id in BUTTONS]
line_config = dict.fromkeys(OFFSETS, INPUT)

# Request the lines, *whew*
request = chip.request_lines(consumer="inky7-buttons", config=line_config)

# refresh inky impression screen
def refreshScreen():
    import weather
    weather.update()

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(event):

    pin = OFFSETS.index(event.line_offset)
    config = configparser.ConfigParser()
    config.read_file(open(configFilePath))

    # Top button(Forecasts)
    if pin == 0:
        config.set("openweathermap", "one_time_message", "")
        config.set("openweathermap", "mode", "4")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    # Second button(Graph mode)
    if pin == 1:
        config.set("openweathermap", "one_time_message", "")
        config.set("openweathermap", "mode", "2")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    # Second button( mode)
    if pin == 2:
        config.set("openweathermap", "one_time_message", "")
        config.set("openweathermap", "mode", "1")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    # 4th button(C/F)
    if pin == 3:
        unit = config.get('openweathermap', 'TEMP_UNIT', raw=False)
        if unit == 'imperial':
            config.set("openweathermap", "one_time_message", "")
            config.set("openweathermap", "TEMP_UNIT", "metric")
        else:
            config.set("openweathermap", "one_time_message", "")
            config.set("openweathermap", "TEMP_UNIT", "imperial")
        
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    try:
        refreshScreen()
    except:
        print("Weather update failed.")
        pass

schedule.every().hour.at(":00").do(refreshScreen)
schedule.every().hour.at(":30").do(refreshScreen)

def button_checker():
    while True:
        for event in request.read_edge_events():
            handle_button(event)

def hourly_update():
    refreshScreen()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    button_thread = Thread(target = button_checker)
    update_thread = Thread(target = hourly_update)
    button_thread.start()
    update_thread.start()