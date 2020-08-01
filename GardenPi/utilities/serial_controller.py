#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
serial_controller.py for usage with neptune/GardenPi V1.0.0
Reads ultrasonic sensors to determine how many gallons we
have in our water tanks. Informational Only.
"""

VERSION = "V1.0.0 (2020-07-31)"


import sys
sys.path.append('/var/www/gardenpi_control/gardenpi')
import serial
import time
from tables import water_tanks
from sqlalchemy import update, select, and_, create_engine
import system_info
from system_logging import setup_logging
from system_logging import read_logging_config
import logging

# Instantiate SQAlchemy Database Engine
engine = create_engine(system_info.sqlalchemy_db_uri)

#Setup Module level logging here. Main logging config in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)


class SerialController:
    STA_OK = 0x00
    STA_ERR_CHECKSUM = 0x01
    STA_ERR_SERIAL = 0x02
    STA_ERR_CHECK_OUT_LIMIT = 0x03
    STA_ERR_CHECK_LOW_LIMIT = 0x04
    STA_ERR_DATA = 0x05

    ''' Define some needed variables'''
    last_operate_status = STA_OK
    distance = 0
    distance_max = 4500
    distance_min = 0
    range_max = 4500

    def __init__(self, tank_name, description, tty, enabled, current_level_inches, current_volume_gallons, gallons_per_inch, max_tank_volume, tank_empty_depth):
        self.tank_name = tank_name
        self.description = description
        self.tty = tty
        self.enabled = enabled
        self.current_volume_gallons = current_volume_gallons
        self.current_level_inches = current_level_inches
        self.gallons_per_inch = gallons_per_inch
        self.max_tank_volume = max_tank_volume
        self.tank_empty_depth = tank_empty_depth
        self.ser = serial.Serial("/dev/" + self.tty, 9600)
        if self.ser.isOpen() != True:
          self.last_operate_status = self.STA_ERR_SERIAL

    @classmethod
    def read_config(cls, tank_name):
      with engine.begin() as conn:
        stmt = select([water_tanks]).where(water_tanks.c.tank_name.in_(tank_name))
        return [
          cls(
            tank_name=row[water_tanks.c.tank_name],
            description=row[water_tanks.c.description],
            tty=row[water_tanks.c.tty],
            enabled=row[water_tanks.c.enabled],
            current_level_inches=row[water_tanks.c.current_level_inches],
            current_volume_gallons=row[water_tanks.c.current_volume_gallons],
            gallons_per_inch=row[water_tanks.c.gallons_per_inch],
            max_tank_volume=row[water_tanks.c.max_tank_volume],
            tank_empty_depth=row[water_tanks.c.tank_empty_depth]
          )
          for row in conn.execute(stmt).fetchall()
        ]

    def check_sum(self, l):
      return (l[0] + l[1] + l[2]) & 0x00ff

    def set_dis_range(self, min, max):
      self.distance_max = max
      self.distance_min = min

    def measure(self):
      data = []
      i = 0
      while self.ser.inWaiting() == 0:
        i += 1
        time.sleep(0.05)
        if i > 4:
          break
      i = 0
      while self.ser.inWaiting() > 0:
        data.append(ord(self.ser.read()))
        i += 1
        if data[0] != 0xff:
          i = 0
          data = []
        if i == 4:
          break
      self.ser.read(self.ser.inWaiting())
      if i == 4:
        sum = self.check_sum(data)
        if sum != data[3]:
          self.last_operate_status = self.STA_ERR_CHECKSUM
        else:
          self.distance = data[1] * 256 + data[2]
          self.last_operate_status = self.STA_OK
        if self.distance > self.distance_max:
          self.last_operate_status = self.STA_ERR_CHECK_OUT_LIMIT
          self.distance = self.distance_max
        elif self.distance < self.distance_min:
          self.last_operate_status = self.STA_ERR_CHECK_LOW_LIMIT
          self.distance = self.distance_min
      else:
        self.last_operate_status = self.STA_ERR_DATA

    def getDistance(self):
        self.measure()
        return self.distance
