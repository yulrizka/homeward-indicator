# Homeward Lamp Indicator

http://labs.yulrizka.com/en/2013/02/homeward-light-indicator-with-raspberrypi-and-commonsense.html

Crontrol A desk lamp that automatically turn on when it's weekday and just left the office.
The idea is to create an indicator so that your beloved ones can be noticed when you have left the office.

This project run on a Raspberry-pi that can connect to [CommonSense](http://www.sense-os.nl/commonsense). The script are written in python based on
Event scripting by Pim Nijdam. https://github.com/pimnijdam/eventScripting

## Installation

To get started install all of the project dependency with:

```
pip install --user git+https://github.com/pimnijdam/eventScripting.git
```

The lamp are controlled with [WiringPi-Python](https://github.com/WiringPi/WiringPi-Python).
