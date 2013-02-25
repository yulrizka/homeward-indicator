#!/usr/bin/python
'''
Created on Feb 17, 2013

@author: pim, ahmy
'''

import senselet
from commonsense import User
from location import Position, isNear, onNear, arriviedAt, departedFrom
import json
import math
from senselet import Event, eventExpression, eventMethod
import eventLogic
import wiringpi
import datetime
import threading
import time

credentials = json.load(open("credentials.json"))
io = None
lightStatus = False

def ioSetup():
  global io
  io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
  io.pinMode(18,io.OUTPUT)
  readLightStatus()

def light(on):
  print "{}: lights {}".format(datetime.datetime.now(), "On" if on else "Off")
  if on:
    status = io.HIGH
    lightStatus = True
  else:
    status = io.LOW
    lightStatus = False

  io.digitalWrite(18, status)

def isLate():
  now = datetime.datetime.now()
  hour = now.hour
  return hour >= 21 or hour <= 9

def readLightStatus():
  lightStatus = io.digitalRead(18)
  return lightStatus

def lightsOffWhenIsLate():
  while True:
    time.sleep(60)
    if isLate() and readLightStatus() == 1:
      print "It's late, turning off lights"
      light(False)

#define our own condition
@eventExpression("onAfterOfficeHour")
def onAfterOfficeHour(date, value):
  dateTime = datetime.datetime.fromtimestamp(date)
  weekday = dateTime.weekday()
  hour = dateTime.hour
  afterOfficeHour =  weekday in range(0,5) and hour >= 17
  print "after office {} result: {}".format(dateTime, afterOfficeHour)
  return value if afterOfficeHour else None

@eventExpression("onNotLate")
def onNotLate(date, value):
  return not isLate()

@eventExpression("turnOnLight")
def turnOnLight(date, value):
  light(True)

def main():
    ioSetup()

    #light(True)
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    putri = User("putri129@gmail.com", credentials["putri129@gmail.com"])
    putri.event().sensor("position", ownedBy="ahmy@sense-os.nl").departedFrom(senseHQ).onAfterOfficeHour().onNotLate().turnOnLight().realTime(60).makeItSo()

    # just turn off the light when it is lage (> 21.00)
    th = threading.Thread(target=lightsOffWhenIsLate)
    th.daemon = True
    th.start()

if __name__ == '__main__':
    main()
