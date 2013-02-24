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

def light(on):
  if on:
    status = io.HIGH
    lightStatus = True
  else:
    status = io.LOW
    lightStatus = False

  io.digitalWrite(18, status)

def isLate():
  now = datetime.datetime.now()
  return now.hour >= 21

def lightsOffWhenIsLate():
  while True:
    time.sleep(60)
    if isLate():
      print "It's late, turning off lights"
      light(False)

#define our own condition
@eventMethod("onAfaterOfficeHour")
def onAfaterOfficeHour(self):
  def onAfaterOfficeHour(date, value):
    dateTime = datetime.datetime.fromtimestamp(date)
    weekday = dateTime.weekday()
    hour = dateTime.hour
    print "{} {}".format(weekday, hour)
    print not weekday in range(0,5) and not hour >= 17
    return value if not weekday in range(0,5) and not hour >= 17 else None
  self.attach(onAfaterOfficeHour)

@eventMethod("onNotLate")
def onNotLate(self):
  def onNotLate(date, value):
    return not isLate()
  self.attach(onNotLate)

@eventExpression("turnOnLight")
def turnOnLight(date, value):
  light(True)

def main():
    ioSetup()

    light(True)
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    putri = User("putri129@gmail.com", credentials["putri129@gmail.com"])
    putri.event().sensor("position", ownedBy="ahmy@sense-os.nl").departedFrom(senseHQ).onAfaterOfficeHour().onNotLate().turnOnLight().realTime(60).makeItSo()

    # just turn off the light when it is lage (> 21.00)
    th = threading.Thread(target=lightsOffWhenIsLate)
    th.daemon = True
    th.start()

if __name__ == '__main__':
    main()
