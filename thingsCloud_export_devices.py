#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import re
import os
import sys
import json
import requests
from requests.cookies import RequestsCookieJar

session = requests.Session()
cookie_jar = RequestsCookieJar()
user = "admin@wicsun.com"
pwd = "123456"

datatype_len = {
	"bool": 1,
	"uint8": 1,
	"int8": 1,
	"uint16": 1,
	"int16": 1,
	"uint32": 2,
	"int32": 2,
	"float": 2
}

# header = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, sdch, br",
#     "Accept-Language": "zh-CN,zh;q=0.8",
#     "Cache-Control": "max-age=0",
#     "Connection": "keep-alive",
#     "Cookie": "_octo=GH1.1.1664649958.1449761838; _gat=1; logged_in=no; _gh_sess=eyJsYXN0X3dyaXRlIjoxNDcyODA4MTE1NzQ5LCJzZXNzaW9uX2lkIjoiZGU3OTQ1MWE0YjQyZmI0NmNhYjM2MzU2MWQ4NzM0N2YiLCJjb250ZXh0IjoiLyIsInNweV9yZXBvIjoiY25vZGVqcy9ub2RlY2x1YiIsInNweV9yZXBvX2F0IjoxNDcyODA3ODg0LCJyZWZlcnJhbF9jb2RlIjoiaHR0cHM6Ly9naXRodWIuY29tLyIsIl9jc3JmX3Rva2VuIjoiTllUd3lDdXNPZmtyYmRtUDdCQWtpQzZrNm1DVDhmY3FPbHJEL0U3UExGaz0iLCJmbGFzaCI6eyJkaXNjYXJkIjpbXSwiZmxhc2hlcyI6eyJhbmFseXRpY3NfbG9jYXRpb25fcXVlcnlfc3RyaXAiOiJ0cnVlIn19fQ%3D%3D--91c34b792ded05823f11c6fe8415de24aaa12482; _ga=GA1.2.1827381736.1472542826; tz=Asia%2FShanghai",
#     "Host": "github.com",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
# }


def export_gates(ioeurl, Authcode):
	url = ioeurl + '/api/method/iot_ui.iot_api.Batch_entry_gates'
	headers = {
		'HDB-AuthorizationCode': Authcode,
		'Content-Type': 'application/json',
		'Accept': 'application/json'}
	response = requests.get(url, headers=headers)
	ret_content = None
	if response:
		ret_content = json.loads(response.content.decode("utf-8"))
	return ret_content


def getToken():
	url = 'http://iot.symgrid.com/api/method/iot_ui.iot_api.get_token'
	headers = {'Content-Type': 'application/x-www-form-urlencoded',
			   'Accept': 'application/json'}
	html = session.get(url, headers=headers)
	# print(json.loads(html.text))
	return json.loads(html.text)['message']


def userpwdLogin():
	url = 'http://iot.symgrid.com/api/method/login'
	headers = {'Content-Type': 'application/x-www-form-urlencoded',
			   'Accept': 'application/json'}
	data = {
		"usr": user,
		"pwd": pwd
	}
	response = session.post(url, headers=headers, data=data)
	ret_content = None
	if response:
		ret_content = response.cookies.get_dict()
	return ret_content


def devices_list():
	url = 'http://iot.symgrid.com/api/method/iot_ui.iot_api.devices_list?filter=online'
	headers = {'Accept': 'application/json'}
	response = session.get(url, headers=headers)
	ret_content = None
	if response:
		# print(dir(response))
		# print(json.loads(response.text))
		ret_content = json.loads(response.text)['message']
	return ret_content


def iot_device_tree(Authcode, gate_sn):
	url = 'http://iot.symgrid.com/api/method/iot_ui.iot_api.gate_device_tree'
	headers = {'Accept': 'application/json', 'X-Frappe-CSRF-Token': Authcode}
	data = {
		"sn": gate_sn
	}
	response = session.get(url, headers=headers, data=data)
	ret_content = None
	# print(response)
	if response:
		r = json.loads(response.text)
		if 'message' in r.keys():
			ret_content = json.loads(response.text)['message']
	return ret_content


def devices_tags(Authcode, gate_sn, dev_sn):
	url = 'http://iot.symgrid.com/api/method/iot_ui.iot_api.gate_device_cfg'
	headers = {'Accept': 'application/json', 'X-Frappe-CSRF-Token': Authcode}
	data = {
		"sn": gate_sn,
		"vsn": dev_sn
	}
	response = session.get(url, headers=headers, data=data)
	ret_content = None
	# print(response)
	if response:
		# print(dir(response))
		# print(json.loads(response.text))
		ret_content = json.loads(response.text)['message']
	return ret_content

def read_gates(path):
	gates_list = []
	stations_name = []
	with open(path, 'r') as csvFile:
		# 读取csv文件,返回的是迭代类型
		reader = csv.reader(csvFile)
		for i, item in enumerate(reader):
			if i == 0 and item[0].lower() != "sn":
				print("CSV file's line 3 format is not correct!")
				return None
			elif i > 0:
				gate = item[0]
				station_name = item[1]
				station_desc = item[2]
				gates_list.append(gate)
				stations_name.append(station_name+station_desc)
	csvFile.close()
	return gates_list, stations_name

def read_tags(path):
	tags_list = []
	with open(path, 'r') as csvFile:
		# 读取csv文件,返回的是迭代类型
		reader = csv.reader(csvFile)
		for i, item in enumerate(reader):
			tag = item[0]
			tags_list.append(tag)
	csvFile.close()
	return tags_list

if __name__ == "__main__":
	cookies = userpwdLogin()
	Authcode = getToken()
	# gates = devices_list()
	gates, stations = read_gates("tunliu_gates_list.csv")
	tunliu_ccd = read_tags("tunliu_ccd.csv")
	tunliu_byc = read_tags("tunliu_byc.csv")
	tunliu_xmz = read_tags("tunliu_xmz.csv")
	# print(tunliu_delta)
	# print(tunliu_byc)
	# os._exit(0)
	datas = []
	modbus_datas = []
	headers = ['地址', '设备ID', '点名', '类型', '点描述', '读写属性', '站信息']
	modbus_datas.append(headers)
	for gindex, k in enumerate(gates):
		# if '2-30002-001824-00323' in k['device_name']:
		# gate_sn = k['device_sn']
		start_addr = 1 + gindex * 1000
		devs_sn = iot_device_tree(Authcode, k)
		if devs_sn:
			# print(devs_sn)
			byc = []
			ccd = []
			xmz = []
			_sn = {}
			for index, sn in enumerate(devs_sn):
				print(index, sn)
				if 'tunliu' in sn:
					if "byc" in sn.lower():
						dev_cfg = devices_tags(Authcode, k, sn)
						if dev_cfg:
							byc = dev_cfg['inputs']
							_sn["byc"] = sn
						pass
					if "ccd" in sn.lower():
						dev_cfg = devices_tags(Authcode, k, sn)
						if dev_cfg:
							ccd = dev_cfg['inputs']
							_sn["ccd"] = sn
						pass
					if "xmz" in sn.lower():
						dev_cfg = devices_tags(Authcode, k, sn)
						if dev_cfg:
							xmz = dev_cfg['inputs']
							_sn["xmz"] = sn
						pass
			if byc:
				addr = start_addr
				print("addr----------------------------------------", addr)
				for t in tunliu_byc:
					# print(t)
					for i in byc:
						if i['vt'] != "string":
							if i['name'] == t:
								# print([addr, _sn["byc"], i['name'], i['vt'], i['desc'], i['rw']])
								datas.append([addr, _sn["byc"], i['name'], i['vt'], i['desc'], i['rw']])
								modbus_datas.append([addr, _sn["byc"], i['name'], i['vt'], i['desc'], i['rw'], stations[gindex]])
								addr = addr + datatype_len[i['vt']]
			if ccd:
				# print(ccd)
				addr = start_addr + 400
				print("addr----------------------------------------", addr)
				for t in tunliu_ccd:
					# print(t)
					for i in ccd:
						if i['vt'] != "string":
							if i['name'] == t:
								# print([addr, _sn["byc"], i['name'], i['vt'], i['desc'], i['rw']])
								datas.append([addr, _sn["ccd"], i['name'], i['vt'], i['desc'], i['rw']])
								modbus_datas.append([addr, _sn["ccd"], i['name'], i['vt'], i['desc'], i['rw'], stations[gindex]])
								addr = addr + datatype_len[i['vt']]
			if xmz:
				addr = start_addr + 700
				print("addr----------------------------------------", addr)
				for t in tunliu_xmz:
					# print(t)
					for i in xmz:
						if i['vt'] != "string":
							if i['name'] == t:
								# print([addr, _sn["byc"], i['name'], i['vt'], i['desc'], i['rw']])
								datas.append([addr, _sn["xmz"], i['name'], i['vt'], i['desc'], i['rw']])
								modbus_datas.append([addr, _sn["xmz"], i['name'], i['vt'], i['desc'], i['rw'], stations[gindex]])
								addr = addr + datatype_len[i['vt']]

	with open('device_mapping.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(datas)

	with open('_Modbus点表.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(modbus_datas)

	# if dev_cfg:
	# 	devno = devno + 1
	# 	addr = 1 + devno * 500
	# 	print("addr----------------------------------------", addr)  # for m, n in dev_cfg.items():
	# 	if m == 'inputs':
	# 		pass
	# headers = ['name', 'desc', 'dt', 'unit', 'saddr', 'fc', 'rate']
	# with open('example.csv', 'w', newline='') as f:
	# 	writer = csv.DictWriter(f, headers)
	# 	writer.writeheader()
	# 	writer.writerows(n)

	# devno = devno + 1
	# for t in tags:
	# 	# print(t)
	# 	for i in n:
	# 		if i['vt'] != "string":
	# 			if i['name']==t:
	# 				print([addr, sn, i['name'], i['vt'], i['desc'], i['rw']])
	# 				datas.append([addr, sn, i['name'], i['vt'], i['desc'], i['rw']])
	# 				addr = addr + datatype_len[i['vt']]
	# with open('device_mapping.csv', 'w', newline='') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerows(datas)
	#
	# with open('_Modbus点表.csv', 'w', newline='') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerows(modbus_datas)
