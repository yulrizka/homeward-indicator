"""
Crappy notifications, just put in here for some experimenting with my iPhone
"""

#import gevent.monkey
#from gevent.pool import Pool
#gevent.monkey.patch_socket()


from multiprocessing import Process, Queue

import httplib
import json
from apns import APNs, Payload
#from applepushnotification import NotificationService, NotificationMessage
import os
import logging
import time

verbose = False
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
WARN_THRESHOLD = 5


class NotificationPusher:
	useSense = False
	def __init__(self, nrConsumers=1, useSense = False, certfile = None, keyfile=None, sandbox = True):
		self.certfile = certfile
		self.keyfile = keyfile
		self.sandbox = sandbox

		#self.pool = Pool(10)
		self.queue = Queue(1000)
		self.processes = []
		if useSense:
			runner = NotificationPusher.runSense
		else:
			runner = NotificationPusher.runSelf
			self.apns = APNs(use_sandbox=self.sandbox, cert_file=self.certfile, key_file=self.keyfile)
			process = Process(name="apns feedback daemon", target=NotificationPusher.runFeedbackCheck, args=(self,))
			process.daemon = True
			process.start()
			self.processes.append(process)
			
		for i in range(nrConsumers):
			process = Process(name="apns sender daemon", target=runner, args=(self,))
			process.daemon = True
			process.start()
			self.processes.append(process)

	def runSense (self):
		while True:
			try:
				(deviceId, userMessage, payload) = self.queue.get()
				notification = {"device_type": "ios",
						"device_id": deviceId,
						"message":{
							"badge":1,
							"sound":"default",
							"alert":userMessage
							}
					}
				NotificationPusher.request('POST', '/jump/push', json.dumps(notification));
			except:
				logger.exception("Exception trying to send push notification via Sense")

	def runSelf (self):
		while True:
			try:
				(deviceId, userMessage, payload) = self.queue.get()
				payload = Payload(alert=userMessage, sound="default", badge=1)
				self.apns.gateway_server.send_notification(deviceId, payload)
			except:
				#Prepare for reconnect
				self.apns._gateway_server = None
				retrySucceed = False
				try:
					self.apns.gateway_server.send_notification(deviceId, payload)
					retrySucceed = True
				except:
					self.apns._gateway_server = None
				#log exception
				logger.exception("{}: Exception trying to send push notification. RetrySucceed={}".format(self.certfile, retrySucceed))


	def runFeedbackCheck (self):
		while True:
			try:
				for (timestamp, devicetoken) in self.apns.feedback_server.items():
					logger.info("{}:got feedback from apple push notification service: ({},{})".format(self.certfile, timestamp, devicetoken))
				time.sleep(5 * 60)
			except:
				#prepare for reconnect
				self.apns._feedback_server = None
				#log exception
				logger.exception("{}: Exception trying to get apple push notification feedback".format(self.certfile))

	@staticmethod
	def request(method,action,body):
		#url = "localhost:5000"
		url = "dev.sense-os.nl"
		headers = {"Content-type": "application/json"}
		conn = httplib.HTTPConnection(url)
		conn.request(method, action, body, headers)
		response = conn.getresponse()
		responseBody = response.read()
		if verbose:
			print "#"*80
			print '{}{}'.format(url,action)
			print response.status, response.reason, responseBody
			print "#"*80

		return responseBody

	def sendNotification(self, deviceId, userMessage, payload=None):
		if self.queue.full():
			logger.critical("{}: notification queue is full. {} items.".format(self.certfile, self.queue.qsize()))
		elif self.queue.qsize() >= WARN_THRESHOLD:
			logger.warning("{}: {} items in notification queue".format(self.certfile, self.queue.qsize()));
			
		self.queue.put((deviceId, userMessage, payload))
		#some monitoring

#notificationPusher= NotificationPusher(1, certfile='certificates/jumpstart_dev_cer.pem', keyfile='certificates/jumpstart_dev_key.pem', sandbox=True)
notificationPusher= NotificationPusher(1, useSense=True)

def sendNotification(deviceId, userMessage=None, payload=None):
	notificationPusher.sendNotification(deviceId, userMessage, payload)
