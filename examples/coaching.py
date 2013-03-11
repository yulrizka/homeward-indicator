'''
Created on Mar 7, 2013

@author: pim
'''
from senselet.events.commonsense import User, getSensorId
from  senselet.core import eventMethod, eventExpression, eventAction
from senselet.actions.mail import *
from datetime import time as dayTime
import datetime
import json
import math
from senselet.events import senseapi

credentials = json.load(open("credentials.json"))

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


api = senseapi.SenseAPI()
api.AuthenticateSessionId(credentials["pimtest2"]["password"])
pim = User.me()

#coaching
pim.event().deviceType("iPhone 4").isIdle().forTime(60*60).onBecomeTrue().onTimeIsBetween(dayTime(11), dayTime(21)).sendMail("pim@sense-os.nl", "Get up", "Move! you lazy couch potato.").realTime(30).makeItSo()

def getOrMake(sensorName):
    try:
        sensorId = getSensorId(pim.api, sensorName)
    except ValueError:
        #doesn't exist, create sensor
        if pim.api.SensorsPost({'sensor': {'name':sensorName, 'device_type':sensorName, 'data_type':'integer'}}):
            sensorId = pim.api.getLocationId()
    return sensorId

activityCountId = getOrMake("daily activity time")

pim.event().sensor("daily activity time").isAbove(45 * 60).onBecomeTrue().sendMail("pim@sense-os.nl", "Goal reached", "You've reached your goal of one hour of activity today!").realTime(30).makeItSo()
pim.event().deviceType("iPhone 4").isActive().forTime(15*60).onBecomeTrue().sendMail("pim@sense-os.nl", "Goal reached", "You reached your goal of 15 minutes continuous activity.").realTime(30).makeItSo()

pim.event().deviceType("iPhone 4").isActive().timeTrue().sumDailyValue().saveToSensor(activityCountId, batchSize=10).realTime(30).makeItSo()
