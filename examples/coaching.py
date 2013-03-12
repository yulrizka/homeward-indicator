'''
Created on Mar 7, 2013

@author: pim
'''
from senselet.events.commonsense import User, getSensorId
from  senselet.core import eventMethod, eventExpression, eventAction
from senselet.actions.mail import *
from datetime import time as dayTime, timedelta
from senselet.events import commonsense
import datetime
import json
import math
from senselet.events import senseapi

credentials = json.load(open("credentials.json"))
api = senseapi.SenseAPI()
if not api.AuthenticateSessionId(credentials["me"]["user"], senseapi.MD5Hash(credentials["me"]["password"])):
    print "Couldn't login: ".format(api.getResponse())
session = commonsense.Session(api)
me = session.me()

#define our own condition
@eventExpression("isAbove")
def isAbove(date, value, threshold):
    return value > threshold

@eventMethod("isIdle")
def isIdle(self):
    self.sensor("linear acceleration")
    def isIdle(date, jsonValue):
        value = json.loads(jsonValue)
        x,y,z = float(value.get("x-axis")), float(value.get("y-axis")), float(value.get("z-axis"))
        
        magnitude = math.sqrt(x**2+y**2+z**2)
        return magnitude < 2
    self.attach(isIdle)

@eventMethod("isActive")
def isActive(self):
    self.isIdle().isFalse()
    
@eventMethod("incrementDailyValue")
def incrementDaylyValue(self, increment):
    state={}
    state['value'] = 0
    state ['lastDay'] = None
    def addValue(date, value, state):
        today = datetime.datetime.fromtimestamp(date).date()
        if today == state['lastDay']:
            state['value'] += increment
        else:
            #another day, reset count
            state['value'] = increment
        state['lastDay'] = today
        return state['value']
    self.attach(addValue, state)
    
@eventMethod("sumDailyValue")
def sumDaylyValue(self):
    state={}
    state['value'] = 0
    state ['lastDay'] = None
    def addValue(date, value, state):
        today = datetime.datetime.fromtimestamp(date).date()
        if today == state['lastDay']:
            state['value'] += value
        else:
            #another day, reset count
            state['value'] = value
        state['lastDay'] = today
        return state['value']
    self.attach(addValue, state)
    
@eventMethod("timeTrue")
def trueForTime(self):
    state={"last":None}
    def trueForTime(date, value,state):
        ret = 0
        if value and state["last"] is not None:
            ret = date - state["last"]
        state["last"] = date if value else None
        return ret
    self.attach(trueForTime,state)


#coaching
me.event().isIdle().forTime(timedelta(hours=1)).onBecomeTrue().onTimeIsBetween(dayTime(11), dayTime(21)).sendMail("pim@sense-os.nl", "Get up", "Move! you lazy couch potato.").realTime(30).makeItSo()

activityCountId = session.createSensorOnce("daily activity time", "daily activity time", "integer")

me.event().sensor("daily activity time").isAbove(45 * 60).onBecomeTrue().sendMail("pim@sense-os.nl", "Goal reached", "You've reached your goal of one hour of activity today!").realTime(30).makeItSo()
me.event().isActive().forTime(timedelta(minutes=15)).onBecomeTrue().sendMail("pim@sense-os.nl", "Goal reached", "You reached your goal of 15 minutes continuous activity.").realTime(30).makeItSo()

me.event().isActive().timeTrue().sumDailyValue().saveToSensor(activityCountId).realTime(30).makeItSo()
