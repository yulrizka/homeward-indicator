'''
Created on Mar 13, 2013

@author: pim
'''
from senselet.core import eventMethod
import json
import math

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