#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ctypes
import sys
import getopt
import os
import json
import re
import configparser
import platform
from time import sleep
from flask import Flask, current_app, g, session, redirect, url_for, escape, request, render_template, make_response
from flask_cors import *
from flask_httpauth import HTTPTokenAuth
import requests
from requests.auth import HTTPBasicAuth
import logging
import inspect

if sys.argv[0] != os.path.split(os.path.realpath(__file__))[1]:
    os.chdir(os.path.split(sys.argv[0])[0])
print("当前工作路径：" + str(os.getcwd()))
if not os.path.exists("log"):
    os.mkdir("log")

app = Flask(__name__)
app.static_folder
CORS(app, supports_credentials=True)
auth = HTTPTokenAuth(scheme='Bearer')
# app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

def _getLogger():
    logger = logging.getLogger('[cfg_Mqtt_modbus]')
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    handler = logging.FileHandler(os.path.join(dirpath, "./log/cfg_Mqtt_modbus.log"))
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def read_cfg(file):
    cfg = configparser.ConfigParser()
    cfg.read(file)
    redis_srv = cfg.get('redis', 'url')
    if redis_srv:
        redis_srv = redis_srv.split('@')[1].split(':')
    mqtt_srv = (cfg.get('mqtt', 'host'), cfg.getint('mqtt', 'port'), cfg.getint('mqtt', 'keepalive'), cfg.get('mqtt', 'user'))
    mbs_cfg = (cfg.get('mbServ', 'host'), cfg.getint('mbServ', 'port'))
    log_level = cfg.get('log', 'level')
    return {"redis": redis_srv, "mqtt": mqtt_srv,"mbServ": mbs_cfg,"log": log_level}

def mod_cfg(file, _cfg):
    cfg = configparser.ConfigParser()
    cfg.read(file)
    for k, v in _cfg.items():
        for p, q in v.items():
            cfg.set(k, p, q)
    cfg.write(open(file, 'w'))

def service_status():
    services = ["mqtt2mbs_Service"]
    services_status = {}
    for s in services:
        cmd1 = 'sc query ' + s + '|find /I "STATE"'
        cmd_ret = os.popen(cmd1).read().strip()
        cmd_ret = re.split('\s+', cmd_ret)
        if len(cmd_ret) > 1:
            services_status[s] = cmd_ret[3]
    return services_status

def service_start():
    services = ["mqtt2mbs_Service"]
    for s in services:
        cmd1 = 'sc start ' + s + '|find /I "STATE"'
        cmd_ret = os.popen(cmd1).read().strip()
        # print('sc resut:', cmd_ret)
        sleep(0.1)

def service_stop():
    services = ["mqtt2mbs_Service"]
    for s in services:
        cmd1 = 'sc stop ' + s
        cmd_ret = os.popen(cmd1).read().strip()
        # print('sc resut:', cmd_ret)
        sleep(0.1)

def enum_file(dirname):
    result = []
    for maindir, subdir, file_name_list in os.walk(dirname):
        pass
    return file_name_list


@auth.verify_token
def verify_token(token):
    if token == "123123123":
        return True
    return False

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")

@app.route('/logfiles')
def logfiles():
    return json.dumps(enum_file("log"))

@app.route('/r_config', methods=('GET', 'POST'))
def r_config():
    return json.dumps(read_cfg("config.ini"))

@app.route('/w_config', methods=('GET', 'POST'))
def w_config():
    if request.method == 'GET':
        return json.dumps({"message": "请使用POST方法"})
    if request.method == 'POST':
        postinfo = request.get_data().decode('utf-8')
        if not postinfo:
            return json.dumps({})
        postinfo = json.loads(postinfo)
        mod_cfg("config.ini", postinfo)
        return json.dumps(read_cfg("config.ini"))


@app.route('/mb_service_status', methods=('GET', 'POST'))
def mb_service_status():
    return json.dumps(service_status())


@app.route('/mb_service_start', methods=('GET', 'POST'))
def mb_service_start():
    service_start()
    sleep(0.5)
    return json.dumps(service_status())


@app.route('/mb_service_stop', methods=('GET', 'POST'))
def mb_service_stop():
    service_stop()
    sleep(0.5)
    return json.dumps(service_status())

@app.route('/mb_service_restart', methods=('GET', 'POST'))
def mb_service_restart():
    service_stop()
    sleep(0.5)
    service_start()
    sleep(0.5)
    return json.dumps(service_status())

@app.route('/log/<path>')
def load_log(path):
    base_dir = str(os.getcwd())
    resp = make_response(open(os.path.join(base_dir + '/log/', path)).read())
    resp.headers["Content-type"]="application/json;charset=UTF-8"
    return resp


@app.route('/api', methods=('GET', 'POST'))
@auth.login_required
def api():
    # print('@@@@@', os.getcwd())
    if request.method == 'GET':
        return json.dumps({"message": "请使用POST方法"})
    if request.method == 'POST':
        postinfo = request.get_data().decode('utf-8')
        postinfo = json.loads(postinfo)
        print(postinfo)
        return json.dumps(postinfo)

if __name__ == '__main__':
    # logger = _getLogger()
    # logger.info("当前工作路径：" + str(os.getcwd()))
    if sys.argv[0] != os.path.split(os.path.realpath(__file__))[1]:
        os.chdir(os.path.split(sys.argv[0])[0])
    app.run(host="127.0.0.1", port=5060, debug=True)