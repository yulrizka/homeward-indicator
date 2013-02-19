'''
Created on Feb 16, 2013

@author: pim
'''
import threading
import Queue
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
        self._inputEvents = []
    
    def attach(self, function, state=None):
        self._pipeline.append((function, state))
        return self
        
    ### Execution methods ###

    """
    Invoked before actually running this event. This method is provided so it can be conveniently overridden by subclasses.
    """
    def _prepare(self):
        pass

    def _run(self):        
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

    def run(self):
        self._prepare()
        self._run()


    """
    DOESN"T WORK, THREAD IS NEVER STOPPED!
    Get values, reusing the run method, at the cost of an extra thread. 
    """
    def _never_stopping_values(self):
        q = Queue.Queue()
        def queueWriter(date,value,state):
            q.put((date,value))
            return value
            
        self.attach(queueWriter)
        self.makeItSo()
        while True:
            item = q.get()
            if item is StopIteration: return
            yield item
    
    """
    Execute and yield values
    """
    def values(self):
        self._prepare()
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
            yield (date,value)
    
    """
    Execute the event in a thread
    """
    def makeItSo(self):
        self._prepare()
        t = threading.Thread(target=self._run)
        t.start()
    
    #on* Operators yield the value when ....
    def onChange(self):
        def func(date,value,state):
            prev = state.get('value')
            changed = prev is None or value != prev
            state['value'] = value
            if changed:
                return value
            else:
                return None
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
                return None
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
            return False
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
    
    ### combine multiple Events ###
