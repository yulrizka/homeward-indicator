### Senselet (working name, need to change) ###

This is an attempt to make it easy to do some scripting with common sense. Actually other inputs / outputs could be easily used as well. This is a prototype that I created due to being frustrated about how hard it is to do some simple things with my sensor data.
The main point is about task description. It should be easy to express task (e.g. if at home and idle for more than an hour send me a notification). How the task is implemented is less important. For now it works with local processing but it might as well instantiate a math service, a trigger and a notification, or even provision a whole storm topology, run on your phone or in the cloud, or partially run on your phone and partially in the cloud. With proper abstraction task description shouldn't depend on where you run things. Lot's of attention has been to syntactic sugar. It should be really easy to define and add your own methods. See the main.py and location.py modules for some inspiration.

Mainly inspired by years of frustration, ORM (thanks SQAlchemy) and the "Code over the air" paper.

Have fun!

### Documentation ###
This is a prototype, don't expect to much documentation here. But for starters
use pip to install the needed packages.
```
pip install --user -r requirements.txt
```

.run runs your task
.makeItSo() makes it happen. It spawns a thread that performs your task
.values() can be used to iterate over all values. (don't worry, values will be requested from the server as needed and in batches)
user.realTime(10) can be used to do realtime processing with data being requested every 10 seconds.

Still interested? Talk to Pim, he wants your input!
