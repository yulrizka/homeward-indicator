'''
Created on Mar 6, 2013

@author: pim
'''

from senselet.core.event import eventMethod
import datetime

@eventMethod("isAfter")
def isAfter(event, after):
    if isinstance(after, datetime.time):
        #Do comparison with time of day, ignore date
        def afterTime(date,value):
            inputDate = datetime.datetime.fromtimestamp(date).time()
            return inputDate > after
        event.attach(afterTime)
    elif isinstance(after, datetime):
        #Do comparison with datetime
        def afterDate(date,value):
            inputDate = datetime.datetime.fromtimestamp(date).time()
            return inputDate > after
        event.attach(afterDate)
    else:
        raise TypeError("Argument is neither datetime.time nor datetime.datetime")

@eventMethod("onAfter")
def onAfter(event, after):
    event.isAfter(after).OnTrue()


@eventMethod("isBefore")
def isBefore(event, before):
    if isinstance(before, datetime.time):
        #Do comparison with time of day, ignore date
        def beforeTime(date,value):
            inputDate = datetime.datetime.fromtimestamp(date).time()
            return inputDate < before
        event.attach(beforeTime)
    elif isinstance(before, datetime):
        #Do comparison with datetime
        def beforeDate(date,value):
            inputDate = datetime.datetime.fromtimestamp(date).time()
            return inputDate < before
        event.attach(beforeDate)
    else:
        raise TypeError("Argument is neither datetime.time nor datetime.datetime")
    
@eventMethod("onBefore")
def onBefore(event, before):
    event.isBefore().onTrue()
    
@eventMethod("timeIsBetween")
def timeIsBetween(event, after, before):
    if isinstance(before, datetime.time) and isinstance(after, datetime.time):
        #Do comparison with time of day, ignore date
        def betweenTime(date,value):
            inputDate = datetime.datetime.fromtimestamp(date).time()
            return inputDate < before and inputDate > after
        event.attach(betweenTime)
    else:
        raise TypeError("Arguments should be datetime.time")

@eventMethod("onTimeIsBetween")
def onTimeIsBetween(event, after, before):
    event.timeIsBetween(after,before).onTrue()
