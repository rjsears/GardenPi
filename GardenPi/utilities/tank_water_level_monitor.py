#!/usr/bin/python3
# -*- coding: utf-8 -*-

#TODO Modify this setup to move non-contact sensors to GPIO expanders via wiringPI!

"""
tank_water_level_monitor.py for use with neptune/GardenPi V1.0.0
Script to monitor tank water levels in real time and switch
water source if we run out of water.
"""

VERSION = "V1.0.0 (2020-07-31)"


import sys
sys.path.append('/var/www/gardenpi_control/gardenpi/utilities')
import threading
from neptune import switch_from_fish_source, get_water_source, toggle_fish_available
from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio
from digitalio import Direction, Pull


nutrient_tank = 0

#Setup our GPIO Expanders here - need to modify this to use wiringpi (maybe?)
i2c = busio.I2C(board.SCL, board.SDA)
mcp3 = MCP23017(i2c, address=0x24)
mcp3.get_pin(nutrient_tank)
mcp3.get_pin(nutrient_tank).direction = Direction.INPUT
mcp3.get_pin(nutrient_tank).pull = Pull.UP

checked = False

def change_water_source():
    """Function to actually change our water source if we run out of water."""
    global checked
    if not checked:
        checked = True
        if (get_water_source()['job_water_source']) == 'fish_water':
            print('switching source')
            switch_from_fish_source()


def run_check():
    """Function that watches our NC liquid level sensors and makes updates based on them."""
    global checked
    if not checked:
        if not mcp3.get_pin(nutrient_tank).value:
            toggle_fish_available(False)
            change_water_source()
    else:
        if mcp3.get_pin(nutrient_tank).value:
            checked = False
            if not (get_water_source()['fish_available']):
                toggle_fish_available(True)
    threading.Timer(.5, run_check).start()



def main():
    run_check()

if __name__ == '__main__':
    main()