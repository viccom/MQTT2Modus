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
from time import sleep, time


class Worker(threading.Thread):
	def __init__(self, log, ioeurl, Authcode):
		threading.Thread.__init__(self)
		self.log = log
		self.data_queue = queue.Queue(10240)
		self.redis_forwarder = redis.Redis.from_url("redis://172.30.0.182:6379" + "/0")
		self.ioeurl = ioeurl or "http://ioe.thingsroot.com"
		self.Authcode = Authcode or "1234567890"

	def run(self):
		dq = self.data_queue
		while True:
			sleep(0.05)
			# process tasks queue
			while not dq.empty():
				value = dq.get()
				if isinstance(value, (list, tuple)):
					try:
						# self.redis_forwarder.set(value[0], value[1][0])
						stra = value[0].split("/", 1)
						device_sn = stra[0]
						strb = stra[0].split(".", 1)
						gate_sn = strb[0]
						output = stra[1]
						val = value[1][0]
						req_id = value[0] + "/set_value/" + str(time())
						datas = {
							"id": req_id,
							"device": gate_sn,
							"data": {
								"device": device_sn,
								"output": output,
								"value": val,
								"prop": "value"
								}
							}
						action_ret = None
						wri_ret = self.post_data_2ioe(datas)
						if wri_ret['message'] == req_id:
							for i in range(4):
								action_ret = self.get_action_result(req_id)
								if action_ret:
									break
								sleep(i + 1)
						if action_ret:
							if action_ret["message"]["result"]:
								self.log.info("1. set value:" + value[0] + "/" + str(value[1][0]) + "/" + "Successful")
							else:
								self.log.error("1. set value:" + value[0] + "/" + str(value[1][0]) + "/" + "Failed")
						else:
							self.log.error("1. set value:" + value[0] + "/" + str(value[1][0]) + "/" + "Failed")
					except Exception as ex:
						self.log.fatal(ex)
						self.log.fatal('set value: Catch an exception.')
				else:
					try:
						# self.redis_forwarder.set(value[0], value[1])
						stra = value[0].split("/", 1)
						device_sn = stra[0]
						strb = stra[0].split(".", 1)
						gate_sn = strb[0]
						output = stra[1]
						val = value[1]
						req_id = value[0] + "/set_value/" + str(time())
						datas = {
							"id": req_id,
							"device": gate_sn,
							"data": {
								"device": device_sn,
								"output": output,
								"value": val,
								"prop": "value"
								}
							}
						action_ret = None
						wri_ret = self.post_data_2ioe(datas)
						if wri_ret['message'] == req_id:
							for i in range(4):
								action_ret = self.get_action_result(req_id)
								if action_ret:
									break
								sleep(i + 1)
						if action_ret:
							if action_ret["message"]["result"]:
								self.log.info("2. set value:" + value[0] + "/" + str(value[1]) + "/" + "Successful")
							else:
								self.log.error("2. set value:" + value[0] + "/" + str(value[1]) + "/" + "Failed")
						else:
							self.log.error("2. set value:" + value[0] + "/" + str(value[1]) + "/" + "Failed")
					except Exception as ex:
						self.log.fatal(ex)
						self.log.fatal('set value: Catch an exception.')

	def append_data(self, tagname, value):
		self.data_queue.put((tagname, value))

	def post_data_2ioe(self, send_data):
		url = self.ioeurl + '/api/method/iot.device_api.send_output'
		headers = {'AuthorizationCode': self.Authcode, 'Content-Type': 'application/json', 'Accept': 'application/json'}
		response = requests.post(url, headers=headers, data=json.dumps(send_data))
		ret_content = None
		if response:
			ret_content = json.loads(response.content.decode("utf-8"))
		return ret_content

	def get_action_result(self, id):
		url = self.ioeurl + '/api/method/iot.device_api.get_action_result?id=' + id
		headers = {'AuthorizationCode': self.Authcode, 'Accept': 'application/json'}
		response = requests.get(url, headers=headers)
		ret_content = None
		if response:
			ret_content = json.loads(response.content.decode("utf-8"))
		return ret_content