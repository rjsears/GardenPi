#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
gardenpi_serial.py for use with neptune/GardenPi V1.0.0
Modified from DFRobot code

"""

VERSION = "V1.0.0 (2020-07-31)"

import serial
import time

class FishWaterTankVolume:
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05
  last_operate_status = STA_OK
  distance = 0
  distance_max = 4500
  distance_min = 0
  range_max = 4500

  def __init__(self):
    self.ser = serial.Serial("/dev/ttySC0", 9600)
    if self.ser.isOpen() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

  def check_sum(self, l):
    return (l[0] + l[1] + l[2])&0x00ff

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
        self.distance = data[1]*256 + data[2]
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



class TankVolume1:
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05
  last_operate_status = STA_OK
  distance = 0
  distance_max = 4500
  distance_min = 0
  range_max = 4500

  def __init__(self):
    self.ser = serial.Serial("/dev/ttySC1", 9600)
    if self.ser.isOpen() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

  def check_sum(self, l):
    return (l[0] + l[1] + l[2])&0x00ff

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
        self.distance = data[1]*256 + data[2]
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

class TankVolume2:
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05
  last_operate_status = STA_OK
  distance = 0
  distance_max = 4500
  distance_min = 0
  range_max = 4500

  def __init__(self):
    self.ser = serial.Serial("/dev/ttySC2", 9600)
    if self.ser.isOpen() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

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

class TankVolume3:
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05
  last_operate_status = STA_OK
  distance = 0
  distance_max = 4500
  distance_min = 0
  range_max = 4500

  def __init__(self):
    self.ser = serial.Serial("/dev/ttySC3", 9600)
    if self.ser.isOpen() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

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