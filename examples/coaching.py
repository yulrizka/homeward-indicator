'''
Created on Mar 7, 2013

@author: pim
'''
from senselet.events.commonsense import User
from  senselet.core import eventMethod, eventExpression, eventAction
from senselet.actions.mail import *
from datetime import time as dayTime
import json
import math

credentials = json.load(open("credentials.json"))

#define our own condition

@eventMethod("isIdle")
def isIdle(self):
    self.sensor("acceleration")
    def isIdle(date, jsonValue):
        value = json.loads(jsonValue)
        x,y,z = float(value.get("x-axis")), float(value.get("y-axis")), float(value.get("z-axis"))
        
        magnitude = math.sqrt(x**2+y**2+z**2)
        return magnitude < 2
    self.attach(isIdle)

pim = User("pimtest2", credentials["pimtest2"]["password"])


#coaching
pim.event().deviceType("iPhone").isIdle().forTime(60*60).onBecomeTrue().timeIsBetween(dayTime(11), dayTime(21)).sendMail("pim@sense-os.nl", "Get up", "Move! you lazy couch potato.").realTime(30).run()