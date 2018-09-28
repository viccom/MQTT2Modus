#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
Publish/Subscribe message broker between Redis and MQTT
'''
import threading
import struct
import json
import re
import os
import logging
import paho.mqtt.client as mqtt

match_value = re.compile(r'^([^/]+)/value')
match_data = re.compile(r'^([^/]+)/data')
match_data_path = re.compile(r'^([^/]+)/([^/]+)/(.+)$')
match_topic = re.compile(r'^([^/]+)/(.+)$')

datatype_len = {
    "uint16": 1,
    "int16": 1,
    "uint32": 2,
    "int32": 2,
    "float": 2
}
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	logging.info("Sub MQTT Connected with result code "+str(rc))
	client.subscribe("+/data")


def on_disconnect(client, userdata, rc):
	logging.info("Sub MQTT Disconnect with result code "+str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	g = match_data.match(msg.topic)
	if g:
		g = g.groups()
		dev = g[0]
		if dev in userdata[1][3]:
			# mm = json.loads(msg.payload.decode('utf-8'))
			# print(dev, mm['input'], mm['data'][1])
			mqclient = userdata[0]
			mqclient.on_mqtt_message(dev, userdata[1], dev, msg.payload.decode('utf-8'))


class MQTTClient(threading.Thread):
	def __init__(self, client, mqttcfg, mbcfg):
		threading.Thread.__init__(self)
		self.client = client
		self.mqttcfg = mqttcfg
		self.mbcfg = mbcfg


	def run(self):
		try:
			mqttc = mqtt.Client(userdata=(self.client, self.mbcfg), client_id="MQTT_TO_Modbus.SUB")
			mqttc.username_pw_set(self.mqttcfg[3], self.mqttcfg[4])
			self.mqttc = mqttc

			mqttc.on_connect = on_connect
			mqttc.on_disconnect = on_disconnect
			mqttc.on_message = on_message

			logging.debug('MQTT Connect to %s:%d', self.mqttcfg[0], self.mqttcfg[1])
			mqttc.connect_async(self.mqttcfg[0], self.mqttcfg[1], self.mqttcfg[2])

			mqttc.loop_forever(retry_first_connection=True)
		except Exception as ex:
			logging.exception('MQTT Exeption')
			os._exit(1)

	def publish(self, *args, **kwargs):
		return self.mqttc.publish(*args, **kwargs)


class SubClient(threading.Thread):
	def __init__(self, mqttcfg, mbcfg):
		threading.Thread.__init__(self)
		self.mqttcfg = mqttcfg
		self.mbcfg = mbcfg


	def run(self):
		mqttc = MQTTClient(self, mqttcfg=self.mqttcfg, mbcfg=self.mbcfg)
		mqttc.start()
		self.mqttc = mqttc

	def on_mqtt_message(self, dev, mbcfg, topic, msg):
		try:
			'''
			Parsing mqtt message and update Modbus
			'''
			# logging.debug('mqtt_message\t%s\t%s\t%s', dev, mbcfg, msg)
			block = mbcfg[0]
			tag_addr = mbcfg[1]
			tag_datatype = mbcfg[2]
			gates_list = mbcfg[3]
			datamsg = json.loads(msg)
			tag_prop = datamsg['input']
			rtval = datamsg['data'][1]

			g = match_value.match(tag_prop)
			if g:
				tagname = topic + "/" + g.groups()[0]
			if tagname in tag_addr.keys():
				if datatype_len[tag_datatype[tagname]] == 1:
					block.setValuesEx(tag_addr[tagname], [rtval])
				elif tag_datatype[tagname] == 'uint32':
					databin = struct.pack('>I', rtval)
					block.setValuesEx(tag_addr[tagname], [struct.unpack('!H', databin[2:4])[0],
					                                   struct.unpack('!H', databin[0:2])[0]])
				elif tag_datatype[tagname] == 'int32':
					databin = struct.pack('>i', rtval)
					block.setValuesEx(tag_addr[tagname], [struct.unpack('!H', databin[2:4])[0],
					                                   struct.unpack('!H', databin[0:2])[0]])
				elif tag_datatype[tagname] == 'float':
					databin = struct.pack('>f', float(rtval))
					block.setValuesEx(tag_addr[tagname], [struct.unpack('!H', databin[2:4])[0],
					                                   struct.unpack('!H', databin[0:2])[0]])


		except Exception as ex:
			logging.exception('Catch an exception.')
