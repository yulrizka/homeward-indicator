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
import sys
import os
from mailer import Mailer

fn = os.path.join(os.path.dirname(__file__), 'credentials.json')
credentials = json.load(open(fn))
io = None
lightStatus = False

def ioSetup():
  global io
  io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
  io.pinMode(18,io.OUTPUT)
  readLightStatus()

def light(on):
  if on:
    status = io.HIGH
    lightStatus = True
  else:
    status = io.LOW
    lightStatus = False

  io.digitalWrite(18, status)
  sys.stdout.write("{}: lights {}\n".format(datetime.datetime.now(), "On" if on else "Off"))

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
      sys.stdout.write("It's late, turning off lights\n")
      light(False)

#define our own condition
@eventExpression("onAfterOfficeHour")
def onAfterOfficeHour(date, value):
  dateTime = datetime.datetime.fromtimestamp(date)
  weekday = dateTime.weekday()
  hour = dateTime.hour
  afterOfficeHour =  weekday in range(0,5) and hour >= 17
  sys.stdout.write ("after office {} result: {}\n".format(dateTime, afterOfficeHour))
  return value if afterOfficeHour else None

@eventExpression("onNotLate")
def onNotLate(date, value):
  return None if isLate() else True

@eventExpression("turnOnLight")
def turnOnLight(date, value):
  light(True)
  message = "lights is on at {}".format(datetime.datetime.now())
  user = credentials["email"]["username"]
  password = credentials["email"]["password"]
  mailer = Mailer(user, password)
  mailer.send("ahmy@sense-os.nl", "Light is on", message)

def main():
    ioSetup()

    # just turn off the light when it is lage (> 21.00)
    th = threading.Thread(target=lightsOffWhenIsLate)
    #th.daemon = True
    th.start()

    #light(True)
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    putri = User("putri129@gmail.com", credentials["putri129@gmail.com"])
    putri.event().sensor("position", ownedBy="ahmy@sense-os.nl").departedFrom(senseHQ).onAfterOfficeHour().onNotLate().turnOnLight().realTime(60).run()


if __name__ == '__main__':
    main()
