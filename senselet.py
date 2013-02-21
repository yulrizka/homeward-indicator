'''
Created on Feb 16, 2013

@author: pim
'''
import threading
import Queue
"""
A proxy to facilitate some weird syntax. Probably a bad idea, don't count on this being around in the future.
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
    def __init__(self, inputData=None):
        self.inputData = inputData
        self._pipeline = []
        self._inputEvents = []
    
    def attach(self, function, *args, **kwargs):
        self._pipeline.append((function, args, kwargs))
        return self
        
    ### Execution methods ###

    """
    Invoked before actually running this event. This method is provided so it can be conveniently overridden by subclasses.
    """
    def _prepare(self):
        structure =  "{}: ".format("Event")
        for (stage, args, kwargs) in self._pipeline:
            structure += " -> {}()".format(stage.__name__)
        print structure

    def _run(self):
        if self.inputData is None:
            raise Exception("No input data for event!")
                  
        for (date,value) in self.inputData():
            stopped = False
            for (stage, args, kwargs) in self._pipeline:
                try:
                    newValue = stage(date,value,*args, **kwargs)
                except TypeError:
                    print "Exception in function {}.".format(stage.__name__)
                    raise
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
        for (date,value) in self.inputData():
            stopped = False
            for (stage, args, kwargs) in self._pipeline:
                try:
                    newValue = stage(date,value,*args, **kwargs)
                except TypeError:
                    print "Exception in function {}.".format(stage.__name__)
                    raise
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
        
"""
Decorator to provide some syntactic sugar. This decorator:
- patches the Event object with the function
- returns self to allow method chaining

example:

@eventMethod("isNear")
def isNear(self,referencePosition):
    self.distanceFrom(referencePosition)
    self.attach(lambda date,distance: distance < 100)

Event().isNear(referencePosition).otherFuncion()

Note that eventMethods are omnipotent, they can have state.

Trust me, the code is fine. Don't mess with it!
"""
def eventMethod(name):
    def wrap(f):
        def wrapped_f(self, *args,**kwargs):
            f(self, *args,**kwargs)
            return self
        print "Declaring method Event.{}".format(name)
        setattr(Event, name, wrapped_f)
        return wrapped_f
    return wrap

"""
Decorator to provide even more syntactic sugar. This decorator:
- patches the Event object with the name
- returns self to allow method chaining
- attaches the function to the Event pipeline

example:

@eventExpression("isNear")
def isNearFunction(date,value,referencePosition)
    return referencePosition.distanceTo(value) < 100

Event().isNear(referencePosition)
Note that eventExpressions are stateless

Trust me, the code is fine. Don't mess with it!
"""
def eventExpression(name):
    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            self.attach(f,*args, **kwargs)
            return self
        setattr(Event, name, wrapped_f)
        print "Declaring expression Event.{}".format(name)
        return wrapped_f
    return wrap
    
@eventMethod("onChanged")
def onChanged(self):
    def func(date,value,state):
        prev = state.get('value')
        changed = prev is None or value != prev
        state['value'] = value
        if changed:
            return value
        else:
            return None
        self.attach(func, {})
    
@eventMethod("onBecomeTrue")
def onBecomeTrue(self):
    state = {'prev':False}
    def onBecomeTrue(date,value,state):
        prev = state.get('prev')
        state['prev'] = value
        if value and not prev:
            return value
        else:
            return None
    self.attach(onBecomeTrue,state)
    
@eventMethod("onBecomeFalse")
def onBecomeFalse(self):
    state = {'prev':True}
    def onBecomeFalse(date,value,state):
        prev = state.get('prev')
        state['prev'] = value
        if not value and prev:
            return value
        else:
            return None
    self.attach(onBecomeFalse,state)

@eventExpression("onTrue")
def onTrue(date,value):
    return True if value else None
    
#is* operators yield whether the condition holds
    
@eventMethod("forTime")
def forTime(self, time):
    def forTime(date,value,state):
        since = state.get("since")
        if value:
            if since is not None:
                return date - since >= time
            else:
                state["since"] = date
        elif since is not None:
            del state["since"]
        return False
    self.attach(forTime, {})

@eventExpression("isFalse")
def isFalse(date,value):
    return not value


#helps to debug
@eventExpression("printValue")
def printValue(date, value):
    print "{}:{}".format(date, value)
    return value

@eventExpression("printMsg")
def printMsg(date, value, msg):
    print msg
    return value