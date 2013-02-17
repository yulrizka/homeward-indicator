'''
Created on Feb 16, 2013

@author: pim
'''

"""
A proxy to facilitate some weird syntax
"""
class Proxy(object):
    def __init__(self, proxied, default=None):
        self.proxied = proxied
        self.default = default

    def __getattr__(self, key):
        try:
            return getattr(self.proxied, key)
        except AttributeError:
            if self.default:
                self.default(key, allowMulti=True)
            return self 

"""
Wrapper for events 
"""
class Event(object):
    def __init__(self, dataGenerator=None):
        self.dataGenerator = dataGenerator
        self._pipeline = []
    
    def attach(self, function, state=None):
        self._pipeline.append((function, state))
        return self
        
    ### Execution methods ###
    #TODO: use decorator to check builder for completeness?

    def values(self):
        for x in self.dataGenerator:
            date = x['date']
            value = x['value']
            stopped = False
            for (stage, state) in self._pipeline:
                newValue = stage(date,value,state)
                if newValue is None:
                    stopped = True
                    break
                else:
                    value = newValue
            if stopped:
                continue
            yield value
        return
    
    #on* Operators yield the value when ....
    def onChange(self):
        def func(date,value,state):
            prev = state.get('value')
            changed = prev is None or value != prev
            state['value'] = value
            if changed:
                return value
            else:
                return
        self.attach(func, state = {})
        return self
    
    def onBecomeTrue(self):
        state = {'prev':False}
        def func(date,value,state):
            prev = state.get('prev')
            state['prev'] = value
            if value and not prev:
                return value
            else:
                return
        self.attach(func, state = state)
        return self
    
    def onTrue(self):
        self.attach(lambda date,value,state: True if value else None)
        return self
    
    #is* operators yield whether the condition holds
    
    def forTime(self, time):
        def func(date,value,state):
            since = state.get("since")
            if value:
                if since is not None:
                    return date - since >= time
                else:
                    state["since"] = date
            elif since is not None:
                del state["since"]
            pass
        self.attach(func, state={})
        return self

    #
    def isNot(self):
        self.attach(lambda date,value,state: not value)
        return self

    #helps to debug
    def printValue(self):
        def printValue(date, value, state):
            print "{}:{}".format(date, value)
            return value
        self.attach(printValue)
        return self
