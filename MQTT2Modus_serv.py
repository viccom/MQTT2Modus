#!/usr/bin/env python
"""
Pymodbus Server With Callbacks
--------------------------------------------------------------------------
This is an example of adding callbacks to a running modbus server
when a value is written to it. In order for this to work, it needs
a device-mapping file.
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
import re
import os
import sys
import json
import logging
from collections import deque
from configparser import ConfigParser
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from pymodbus.compat import iteritems, iterkeys, itervalues, get_next
import paho.mqtt.client as mqtt
import atexit
import signal
import traceback
import requests
import binascii
import struct
import redis
from sub_Mqtt_modbus import SubClient
from sub_modbus_write import Worker

# --------------------------------------------------------------------------- #
# import the python libraries we need
# --------------------------------------------------------------------------- #
from multiprocessing import Queue, Process
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
import inspect


if sys.argv[0] != os.path.split(os.path.realpath(__file__))[1]:
    os.chdir(os.path.split(sys.argv[0])[0])
print("当前工作路径：" + str(os.getcwd()))

if not os.path.exists("log"):
    os.mkdir("log")
config = ConfigParser()
config.read('config.ini')
log_level = config.get('log', 'level')
level = logging.getLevelName(log_level)


logging.basicConfig()
log = logging.getLogger()
#输出到屏幕
ch = logging.StreamHandler()
ch.setLevel(level)
#输出到文件
# fh = logging.FileHandler("log2.log")
fh = RotatingFileHandler('./log/log.log',  mode='a+', maxBytes=100*1024, backupCount=9, delay=True)

fh.setLevel(level)
#设置日志格式
fomatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(module)s:%(message)s')
ch.setFormatter(fomatter)
fh.setFormatter(fomatter)
# log.addHandler(ch)
log.addHandler(fh)
log.setLevel(level)

# this_file = inspect.getfile(inspect.currentframe())
# dirpath = os.path.abspath(os.path.dirname(this_file))
# handler = log.FileHandler(os.path.join(dirpath, "MQTT2Modus_Serv.log"))
# formatter = log.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
# handler.setFormatter(formatter)


# --------------------------------------------------------------------------- #
# change workdir to pyfile path
# --------------------------------------------------------------------------- #
# os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
match_topic = re.compile(r'^([^/]+)/(.+)$')
match_value = re.compile(r'^([^/]+)/value')

datatype_len = {
    "bool": 1,
    "uint8": 1,
    "int8": 1,
    "uint16": 1,
    "int16": 1,
    "uint32": 2,
    "int32": 2,
    "float": 2,
    "uint64": 4,
    "int64": 4,
    "double": 4
}

def term_sig_handler(signum, frame):
    log.info('catched singal: %d' % signum)
    os._exit(0)

@atexit.register
def atexit_fun():
    log.info('i am exit, stack track:')
    exc_type, exc_value, exc_tb = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_tb)

# --------------------------------------------------------------------------- #
# create your custom data block with callbacks
# --------------------------------------------------------------------------- #

class CallbackDataBlock(ModbusSparseDataBlock):
    """ A datablock that stores the new value in memory
    and passes the operation to a message queue for further
    processing.
    """

    def __init__(self, devices, taginfo, redis_rtdb, gates_list, queue):
        """
        """
        self.devices = devices
        self.queue = queue
        self.tag_addr = taginfo[0]
        self.tag_datatype = taginfo[1]
        self.tag_rw = taginfo[2]
        self.redis_rtdb = redis_rtdb
        self.gates_list = gates_list
        values = {k: 0 for k in devices.keys()}
        for _g in self.gates_list:
            try:
                r_redis = self.redis_rtdb.hgetall(_g)
                logging.info("redis server Connected")
            except Exception as ex:
                log.fatal('redis server Exeption!')
                os._exit(1)
            if r_redis:
                for r, s in r_redis.items():
                    rtval = eval(s.decode('utf-8'))[1]
                    g = match_value.match(r.decode('utf-8'))
                    if g:
                        tag = _g + "/" + g.groups()[0]
                    if tag in self.tag_addr.keys():
                        # print(g[0], self.tag_addr[g[0]], rtval)
                        if self.tag_datatype[tag] == 'int8':
                            databin = struct.pack('>h', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin)[0]
                        if self.tag_datatype[tag] == 'int16':
                            databin = struct.pack('>h', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin)[0]
                            pass
                        elif self.tag_datatype[tag] == 'uint32':
                            databin = struct.pack('>I', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        elif self.tag_datatype[tag] == 'int32':
                            databin = struct.pack('>i', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        elif self.tag_datatype[tag] == 'uint64':
                            databin = struct.pack('>Q', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[6:8])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[4:6])[0]
                            values[self.tag_addr[tag] + 2] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 3] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        elif self.tag_datatype[tag] == 'int64':
                            databin = struct.pack('>q', int(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[6:8])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[4:6])[0]
                            values[self.tag_addr[tag] + 2] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 3] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        elif self.tag_datatype[tag] == 'float':
                            databin = struct.pack('>f', float(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        elif self.tag_datatype[tag] == 'double':
                            databin = struct.pack('>d', float(rtval))
                            values[self.tag_addr[tag]] = struct.unpack('!H', databin[6:8])[0]
                            values[self.tag_addr[tag] + 1] = struct.unpack('!H', databin[4:6])[0]
                            values[self.tag_addr[tag] + 2] = struct.unpack('!H', databin[2:4])[0]
                            values[self.tag_addr[tag] + 3] = struct.unpack('!H', databin[0:2])[0]
                            pass
                        else:
                            values[self.tag_addr[tag]] = int(rtval)
        values[0xbeef] = len(values)  # the number of devices
        super(CallbackDataBlock, self).__init__(values)

    def setValues(self, address, value):
        """ Sets the requested values of the datastore
        :param address: The starting address
        :param values: The new values to be set
        """
        # print("@@@@@@@@@@@@@", address, value)
        # print("self.tag_rw", self.tag_rw)
        # super(CallbackDataBlock, self).setValues(address, value)
        self.queue.append_data(self.devices.get(address, None), value)
        # self.queue.put((self.devices.get(address, None), value))

    def setValuesEx(self, address, values):
        ''' Sets the requested values of the datastore

        :param address: The starting address
        :param values: The new values to be set
        '''
        if isinstance(values, dict):
            for idx, val in iteritems(values):
                self.values[idx] = val
        else:
            if not isinstance(values, list):
                values = [values]
            for idx, val in enumerate(values):
                self.values[address + idx] = val

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #


def rescale_value(value):
    """ Rescale the input value from the range
    of 0..100 to -3200..3200.
    :param value: The input value to scale
    :returns: The rescaled value
    """
    s = 1 if value >= 50 else -1
    c = value if value < 50 else (value - 50)
    return s * (c * 64)

def device_writer(queue, tags):
    """ A worker process that processes new messages
    from a queue to write to device outputs
    :param queue: The queue to get new messages from
    """
    redis_forwarder = redis.Redis.from_url("redis://172.30.0.182:6379" + "/0")
    while True:
        device, value = queue.get()
        scaled = rescale_value(value[0])
        log.debug("Write(%s) = %s" % (device, value))
        print("Write(%s) = %s" % (device, value))
        print("tags", tags)
        if not device:
            continue
        redis_forwarder.set(device, value)
        # do any logic here to update your devices

# --------------------------------------------------------------------------- #
# initialize your device map
# --------------------------------------------------------------------------- #
def get_devices_list(path):
    iot_devices = []
    with open(path) as stream:
        for line in stream:
            piece = line.strip().split(',')
            if piece[1] not in iot_devices:
                iot_devices.append(piece[1])
    return iot_devices

def read_device_map(path):
    devices = {}
    with open(path) as stream:
        for line in stream:
            piece = line.strip().split(',')
            devices[int(piece[0])] = piece[1].strip() + "/" + piece[2].strip()
            if datatype_len[piece[3]] == 2:
                devices[int(piece[0]) + 1] = piece[1].strip() + "/" + piece[2].strip()
    return devices


def tag_addr_map(path):
    tag_addr = {}
    with open(path) as stream:
        for line in stream:
            piece = line.strip().split(',')
            tag_addr[piece[1].strip() + "/" + piece[2].strip()] = int(piece[0])
    return tag_addr


def tag_datatype_map(path):
    tag_datatype = {}
    with open(path) as stream:
        for line in stream:
            piece = line.strip().split(',')
            tag_datatype[piece[1].strip() + "/" + piece[2].strip()] = piece[3]
    return tag_datatype

def tag_rw_map(path):
    tag_rw = {}
    with open(path) as stream:
        for line in stream:
            piece = line.strip().split(',')
            tag_rw[piece[1].strip() + "/" + piece[2].strip()] = piece[5]
    return tag_rw

def run_callback_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    log.info("MQTT2Modbus Server initing---------------------------------------------------")
    config.read('config.ini')
    redis_srv = config.get('redis', 'url')
    mqtt_srv = (config.get('mqtt', 'host'), config.getint('mqtt', 'port'), config.getint('mqtt', 'keepalive'), config.get('mqtt', 'user'), config.get('mqtt', 'pwd'))
    mbs_cfg = (config.get('mbServ', 'host'), config.getint('mbServ', 'port'))
    log_level = config.get('log', 'level')
    Authcode = config.get('cloud', 'Authcode')

    level = logging.getLevelName(log_level)
    log.setLevel(level)
    redis_rtdb = redis.Redis.from_url(redis_srv + "/12")

    gates_list = get_devices_list("device_mapping.csv")
    # print("gates_list", gates_list)
    queue = Queue()
    devices = read_device_map("device_mapping.csv")
    # print("devices", devices)
    tag_addr = tag_addr_map("device_mapping.csv")
    tag_datatype = tag_datatype_map("device_mapping.csv")
    tag_rw = tag_rw_map("device_mapping.csv")
    # print("tag_addr", tag_addr)
    # print("tag_datatype", tag_datatype)

    writer = Worker(log, "http://ioe.thingsroot.com", Authcode)
    writer.start()
    block = CallbackDataBlock(devices, (tag_addr, tag_datatype, tag_rw), redis_rtdb, gates_list, writer)

    # block = CallbackDataBlock(devices, (tag_addr, tag_datatype, tag_rw), redis_rtdb, gates_list, queue)
    # print("block", block)
    store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    context = ModbusServerContext(slaves=store, single=True)

    redis_rtdb.connection_pool.disconnect()
    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'thingsroot'
    identity.ProductCode = 'MBS'
    identity.VendorUrl = 'http://cloud.thingsroot.com/'
    identity.ProductName = 'thingsroot modbus Server'
    identity.ModelName = 'thingsroot modbus Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    # time = 2  # 5 seconds delay
    # loop = LoopingCall(f=updating_writer, a=(block, tag_addr, tag_datatype, redis_rtdb, gates_list))
    # loop.start(time, now=False)  # initially delay by time

    # sub = SubClient(mqttcfg=mqtt_srv, mbcfg=(block, tag_addr, tag_datatype, gates_list))
    # sub.start()

    # p = Process(target=device_writer, args=(queue, tag_datatype))
    # p.start()

    log.info("Starting the MQTT2Modbus Server")
    StartTcpServer(context, identity=identity, address=mbs_cfg)


if __name__ == "__main__":
    # signal.signal(signal.SIGTERM, term_sig_handler)
    # signal.signal(signal.SIGINT, term_sig_handler)

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, term_sig_handler)
    run_callback_server()
