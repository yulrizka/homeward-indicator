'''
Created on Feb 17, 2013

@author: pim
'''
from math import radians, cos, sin, asin, sqrt
import json
from geopy import geocoders
import senselet

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km * 1000

class Position(object):
    def __init__(self, *args, **kwargs):
        address = kwargs.get("address")
        jsonvalue = kwargs.get("json")
        
        if len(args) == 2:
            self.lat = args[0]
            self.lon = args[1]
        elif address is not None:
            g = geocoders.Google()
            place, (lat, lon) = g.geocode(address)
            self.lat = lat
            self.lon = lon
        elif jsonvalue is not None:
            value = json.loads(jsonvalue)
            self.lat = float(value['latitude'])
            self.lon = float(value['longitude'])
        else:
            raise Exception("Wrong init")
        
    def distance(self, pos2):
        return distance(self, pos2)
    

def distance(pos1,pos2):
        return haversine(pos1.lat,pos1.lon, pos2.lat,pos2.lon)

@senselet.eventExpression("distanceTo")
def distanceTo(date,value,refPos):
    x = json.loads(value)
    pos = Position(float(x['latitude']), float(x['longitude']))
    return distance(pos, refPos)

@senselet.eventMethod("onNear")
def onNear(self,pos,radius=200):
    self.sensor("position")
    def onNear(date,x,pos):
        return x if pos.distance(Position(json=x)) < radius else None
    self.attach(onNear)


@senselet.eventMethod("isNear")
def isNear(self,pos,radius=200):
    def isNear(date,value,pos):
        return pos.distance(Position(json=value)) < radius
    self.attach(isNear,pos)    

@senselet.eventMethod("arrivedAt")
def arriviedAt(self, location):
    self.isNear(location).forTime(2*60).onBecomeTrue()    

@senselet.eventMethod("departedFrom")
def departedFrom(self, location):
    return self.isNear(location).forTime(2*60).onBecomeFalse()
