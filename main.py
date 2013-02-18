'''
Created on Feb 17, 2013

@author: pim
'''

from commonsense import User, getSensorId
from location import Position
import senselet
import senseapi
import json
import datetime

credentials = json.load(open("credentials.json"))

#define our own condition
def isNear(self,pos):
    self.distanceFrom(pos)
    self.attach(lambda date,distance,state: distance < 200)
    return self
User.isNear = isNear

def onNear(self,pos):
    self.attach(lambda date,x,state: x if pos.distance(Position(json=x)) < 200 else None)
    return self
User.onNear = onNear

def isIdle(self):
    self.sensor("acceleration")
    self.attach(lambda date,x,state: x < 1)
    return self
User.isIdle = isIdle


def main():

    deviceToken = "58ceb9c67321fecc125f01aa6828ccec7b87795e6ba74a7b9fe0404f9d77d5b4"
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    pim = User("pimtest2", credentials["pimtest2"]["password"])
    pim = senselet.Proxy(pim,pim.sensor)
    pim.realTime(30)
    
    pim.position.isNear(senseHQ).forTime(2*60).onBecomeTrue().sendNotification(deviceToken, "Welcome at sense! ").makeItSo()
    #no reuse...
    pim = User("pimtest2", credentials["pimtest2"]["password"])
    pim.realTime(30).isIdle().forTime(60*60).onBecomeTrue().sendNotification(deviceToken, "Couch potato!").makeItSo()

if __name__ == '__main__':
    main()
