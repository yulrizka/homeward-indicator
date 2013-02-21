'''
Created on Feb 17, 2013

@author: pim
'''

import senselet
from commonsense import User
from location import Position, isNear, onNear, arriviedAt, departedFrom
import json
import math
from senselet import Event, eventExpression, eventMethod
import eventLogic

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
    
@eventExpression("isAbove")
def isAbove(date,value, threshold):
    return value > threshold

@eventMethod("isAggresionDetected")
def isAggresionDetected(self):
    self.sensor("noise_sensor").isAbove(70)
    

def timeoutDemo(user1,user2):
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    
    #define when a timeout is needed
    user1IsAtSense = user1.event().isNear(senseHQ)
    user2IsAtSense = user2.event().isNear(senseHQ)
    needTimeout = user1IsAtSense.andEvent(user2IsAtSense).andEvent(user1.event().isAggresionDetected()).forTime(60).onBecomeTrue()
    
    #define action upon timeout
    needTimeout.printMsg("Houston we have a problem!")
    
    #event to cooldown
    user1IsCool = user1.event().isNear(senseHQ).isFalse().forTime(10*60)
    user2IsCool = user2.event().isIdle().forTime(10*60)

    cooledDownEvent = needTimeout.andEvent(user1IsCool).andEvent(user2IsCool)
    cooledDownEvent.onBecomeTrue().printMsg("Both users are cooled down.")
    
    #and make the events happen
    cooledDownEvent.makeItSo()


def main():
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    
    pim = User("pimtest2", credentials["pimtest2"]["password"])
    jp = User("jp@sense-os.nl", credentials["jp@sense-os.nl"]["password"])
    deviceToken = "58ceb9c67321fecc125f01aa6828ccec7b87795e6ba74a7b9fe0404f9d77d5b4"
    
    #some location based triggers
    pim.event().deviceType("iPhone").arrivedAt(senseHQ).printMsg("Welcome at Sense!").makeItSo()
    pim.event().deviceType("iPhone").departedFrom(senseHQ).printMsg("See you later, alligator!").makeItSo()
    
    #coaching
    pim.event().deviceType("iPhone").isIdle().forTime(60*60).onBecomeTrue().printMsg("Couch potato!").sendNotification(deviceToken,  "Couch potato!").makeItSo()

    #warning signal
    pim.event().deviceType("iPhone").isNear(senseHQ).andEvent(jp.event().isNear(senseHQ)).onBecomeTrue().printMsg("Run for your live!").makeItSo()
    
    #trapped
    pim.event().deviceType("iPhone").isNear(senseHQ).andEvent(jp.event().isNear(senseHQ)).forTime(5 * 60).onBecomeTrue().printMsg("You're trapped!").makeItSo()

    #no reuse...
    #pim.newEvent().realTime(30).isIdle().forTime(60*60).onBecomeTrue().sendNotification(deviceToken, "Couch potato!").makeItSo()

if __name__ == '__main__':
    #pim = User("pimtest2", credentials["pimtest2"]["password"])
    #jp = User("jp@sense-os.nl", credentials["jp@sense-os.nl"]["password"])
    #timeoutDemo(pim,jp)
    main()
