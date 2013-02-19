'''
Created on Feb 17, 2013

@author: pim
'''

import senselet
from commonsense import User
from location import Position
import json
import math
from senselet import eventExpression, eventMethod

credentials = json.load(open("credentials.json"))

#define our own condition
@eventExpression("onNear")
def onNear(date,x,pos):
    return x if pos.distance(Position(json=x)) < 200 else None

@eventExpression("isNear")
def isNear(date, value, pos):
    return pos.distance(Position(json=value)) < 200

@eventMethod("isIdle")
def isIdle(self):
    self.sensor("acceleration")
    def func(date, x):
        value = json.loads(x)
        magnitude = math.sqrt(float(value["x-axis"])**2 + float(value["y-axis"])**2 + float(value["z-axis"])**2)
        return magnitude < 2
    self.attach(func)


def main():

    deviceToken = "58ceb9c67321fecc125f01aa6828ccec7b87795e6ba74a7b9fe0404f9d77d5b4"
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    pim = User("pimtest2", credentials["pimtest2"]["password"])
    pim = senselet.Proxy(pim,pim.sensor)
    pim.realTime(30)
    
    
    pim.position.isNear(senseHQ).forTime(2*60).onBecomeTrue().sendNotification(deviceToken, "Welcome at Sense! ").makeItSo()
    pim.position.isNear(senseHQ).forTime(2*60).onBecomeFalse().sendNotification(deviceToken, "Goodbye Sense! ").makeItSo()
    #no reuse...
    pim = User("pimtest2", credentials["pimtest2"]["password"])
    pim.realTime(30).isIdle().forTime(60*60).onBecomeTrue().sendNotification(deviceToken, "Couch potato!").makeItSo()

if __name__ == '__main__':
    main()
