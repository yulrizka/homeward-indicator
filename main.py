'''
Created on Feb 17, 2013

@author: pim
'''

from commonsense import User
from location import Position
import senselet
import senseapi
import json

def main():
    
    credentials = json.load(open("credentials.json"))
    
    #define our own condition
    def isNear(self,pos):
        self.distanceFrom(pos)
        self.attach(lambda date,distance,state: distance < 200)
        return self
    User.isNear = isNear

    def onNear(self,pos):
        self.attach(lambda date,x,state: x if pos.distance(Position(json=x)) < 1000 else None)
        return self
    User.onNear = onNear
    
    
    senseHQ = Position(address="Lloydstraat 5, Rotterdam, Netherlands")
    pim = User(credentials["username"], credentials["password"])
    pim = senselet.Proxy(pim,pim.sensor)
    #pim.realTime(60)
    
    #pim.realTime(5)
    #for x in pim.sensor("accelerometer").printValue().realTime(1).values():
    #    pass
    deviceToken = "58ceb9c67321fecc125f01aa6828ccec7b87795e6ba74a7b9fe0404f9d77d5b4"
    for x in pim.position.isNear(senseHQ).forTime(2*60).onBecomeTrue().sendNotification(deviceToken, "Welcome at sense! ").values():
        print "Welcome at sense"
        

    #    p = Alias(pim.position.lastValue)
    #    pim.position.isNear(pimHQ).forTime(5*60).onBecomeTrue().sendNotification(deviceToken, "Arrived at {}".aliasFormat(p.address()))
    """
    api = senseapi.SenseAPI()
    api.AuthenticateSessionId(pim.username, senseapi.MD5Hash(pim.password))
    if not api.SensorsPost({'sensor':{'name':'position', 'device_type':'near Sense HQ', 'data_type':'json', 'data_structure':'{"longitude":"float","latitude":"float","accuracy":"float"}'}}):
        raise Exception("Failed to create sensor: {}".format(api.getResponse()))
    print api.getResponse()
    sensorId = api.getLocationId()
    for x in pim.position.onNear(senseHQ).saveToSensor(sensorId).values():
       pass
   """

if __name__ == '__main__':
    main()