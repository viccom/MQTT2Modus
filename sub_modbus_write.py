#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
response Modbus 05/0F/06/10message and Write to Device
'''
import threading
import queue
import redis
import struct
import json
import re
import os
import requests
from time import sleep


class Worker(threading.Thread):
	def __init__(self, log):
		threading.Thread.__init__(self)
		self.log = log
		self.data_queue = queue.Queue(10240)
		self.redis_forwarder = redis.Redis.from_url("redis://172.30.0.182:6379" + "/0")

	def run(self):
		dq = self.data_queue
		while True:
			sleep(0.05)
			# process tasks queue
			while not dq.empty():
				value = dq.get()
				if isinstance(value, (list, tuple)):
					self.log.info("write value:"+value[0]+","+str(value[1][0]))
					try:
						self.redis_forwarder.set(value[0], value[1][0])
					except Exception as ex:
						self.log.fatal('Catch an exception.')
				else:
					self.log.info("write value:"+value[0]+","+str(value[1]))
					try:
						self.redis_forwarder.set(value[0], value[1])
					except Exception as ex:
						self.log.fatal('Catch an exception.')

	def append_data(self, tagname, value):
		self.data_queue.put((tagname, value))