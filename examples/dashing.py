'''
Created on Mar 10, 2013

@author: pim
'''
from senselet.core import Event, eventExpression, eventMethod
from senselet.events import commonsense
from senselet.events import senseapi
import json
import requests


credentials = json.load(open("credentials.json"))
api = senseapi.SenseAPI()
if not api.AuthenticateSessionId("pimtest2",senseapi.MD5Hash(credentials["pimtest2"]["password"])):
    print "Couldn't login: ".format(api.getResponse())
session = commonsense.Session(api)
me = session.me()

#widgetBaseUrl = "http://pimdashboard.herokuapp.com:80/widgets/"
widgetBaseUrl = "http://localhost:3030/widgets/"
oauthToken = "YOUR_AUTH_TOKEN"
@eventExpression("toWidget")
def toWidget(date,value, widget):
    body = {"auth_token": oauthToken, "value": int(round(float(value)/60))}
    requests.post(widgetBaseUrl+widget, data=json.dumps(body))
    return value

@eventExpression("karmaToWidgetList")
def karmaToWidgetList(date, value, widget):
    items = []
    for user in value:
        items.append({"label":user,"value":value[user]})
    body = {"auth_token": oauthToken, "items": items}
    print body
    requests.post(widgetBaseUrl+widget, data=json.dumps(body))
    return value
    

#me.event().sensor("karma (QA)").description("sense-android-library").karmaToWidgetList("karma_list").run()
me.event().sensor("daily activity time").toWidget("time_active").realTime(30,fromDate=0).run()