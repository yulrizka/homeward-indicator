'''
Created on Feb 16, 2013

@author: pim
'''

import json
import senseapi
import time
import senselet
import notifications


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.api = senseapi.SenseAPI()
        self.api.AuthenticateSessionId(username, senseapi.MD5Hash(password))

    def event(self):
        return UserEvent(self)
    
class UserEvent(senselet.Event):
    def __init__(self, user):
        super(UserEvent, self).__init__()
        self.api = user.api
        self._sensors = []
        self._deviceType = None
        self._refreshInterval = None
        self._fromDate = None

    ### Event builder methods ###    
    def sensors(self, names, allowMulti=False):
        if len(self._sensors) > 0 :
            raise Exception('Event error. sensor already set')
        self._sensors.extend(names)

    def sensor(self, name, allowMulti=False):
        if not allowMulti and len(self._sensors) > 0 :
            raise Exception('Event error. sensor already set')
        self._sensors.append(name)
        
        return self
    
    def deviceType(self, deviceType):
        self._deviceType = deviceType
        return self
    
    def realTime(self, interval, fromDate=None):
        self._refreshInterval = interval
        self._fromDate = fromDate
        return self
    
    
    ### Actions ###
    def saveToSensor(self, sensorId): 
        state = {}
        state["sensorId"] = sensorId
        def func(date, value, state):
            sensorId = state["sensorId"]
            par = {'data':[{'value':value, 'date':date}]}
            if not self.api.SensorDataPost(sensorId, par):
                raise Exception("Couldn't post to sensor. Error: {}".format(self.api.getResponse()))
            return value
        self.attach(func, state=state)
        return self
    
    def sendNotification(self, deviceToken, message):
        state = {"deviceToken":deviceToken, "message":message}
        def func(date, value, state):
            deviceToken = state["deviceToken"]
            message = state["message"]
            notifications.sendNotification(deviceToken, message)
            return value
        self.attach(func, state=state)
        return self


    
    #override
    def _prepare(self):
        super(UserEvent, self)._prepare()
        if self._refreshInterval is not None and self._fromDate is None:
            fromDate = time.time()
        else:
            fromDate = self._fromDate
        sensorId = getSensorId(self.api, self._sensors[0], self._deviceType)
        def gen():
            return getSensorData(self.api, sensorId, fromDate=fromDate, refreshInterval=self._refreshInterval)
        self.inputData = gen

def getDataFromFile(dataFile):
    json_data=open(dataFile)
    data = json.load(json_data)
    json_data.close()
    for x in data['data']:
        yield (x['date'], x['value'])
        
def getSensorId(api, sensorName, deviceType=None):
    #find sensor
    if not api.SensorsGet({'per_page':1000, 'details':'full'}):
            raise Exception("Couldn't get sensors. {}".format(api.getResponse()))
    sensors = json.loads(api.getResponse())['sensors']
    correctSensors = filter(lambda x: x['name'] == sensorName, sensors)
    if deviceType:
        correctSensors = filter(lambda x: x.has_key("device") and x['device']['type'] == deviceType, correctSensors)
    if len(correctSensors) == 0:
        raise ValueError("Sensor {} not found!".format(sensorName))
    sensorId = correctSensors[-1]["id"]
    return sensorId

def getSensorData(api, sensorId, fromDate=None, refreshInterval=None):
    par= {'sort': 'ASC'}
    if fromDate is not None:
        par['start_date'] = fromDate
    par['per_page'] = 1000

    first = True
    while (True):
        if not api.SensorDataGet(sensorId, par): #TODO check status code
            print "Error: " + repr(api.getResponse());
            print "Waiting 30 seconds and try again"
            time.sleep(30)
            continue
        response = json.loads(api.getResponse())
        
        #yield each data point
        if first:
            for x in response['data']: yield (x['date'], x['value'])
        elif len(response['data']) >= 2:
            for x in response['data'][1:]: yield (x['date'], x['value'])
        
        #see whether all data is gotten
        nr = len(response['data'])
        if (nr < par['per_page']):
            #all data retrieved
            if refreshInterval is None:
                break
            else:
                time.sleep(refreshInterval)
                
        first = False
        if len(response['data']) > 0:
            par['start_date'] = response['data'][-1]['date']
            
            