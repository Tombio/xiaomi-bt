#!/usr/bin/python3

from bluepy import btle
from time import sleep
import binascii

from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS


import threading
import asyncio
import configparser
from functools import partial
import time

class XiaoMiTemp(btle.DefaultDelegate):
    def __init__(self,write_client,location):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
        self.write_client = write_client
        self.LOC=location
        print('Delegate initilized')

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print('notification received')
        databytes=bytearray(data)
        print(binascii.hexlify(databytes))
        temp = int.from_bytes(databytes[0:2],"little")/100
        humid = int.from_bytes(databytes[2:3],"little")
        battery = int.from_bytes(databytes[3:5],"little")/1000
        
        data1 = "{} temperature={}".format(self.LOC,temp)
        data2 = "{} humidity={}".format(self.LOC,humid)
        data3 = "{} battery={}".format(self.LOC,battery)
        print(data1)
        print(data2)
        print(data3)
       
        p = Point("temperature").tag("location", self.LOC).field("value", temp)
        self.write_client.write(bucket="homemeasurements", org="home", record=p)
        p = Point("humidity").tag("location", self.LOC).field("value", humid)
        self.write_client.write(bucket="homemeasurements", org="home", record=p)
        p = Point("battery").tag("location", self.LOC).field("value", battery)
        self.write_client.write(bucket="homemeasurements", org="home", record=p)
    
class Worker(threading.Thread):
    def __init__(self, write_client, address, location):
        super(Worker, self).__init__()
        self.write_client = write_client
        self.address = address
        self.location = location

    def run(self):
        print(f'Start listening device in {self.location}: with address {self.address}')
    
        while True:
            print(f'start loop for {self.location}')
            try:        
                p = btle.Peripheral( )
                p.setDelegate(XiaoMiTemp(self.write_client, self.location)) 
                p.connect(self.address)
                p.waitForNotifications(20.0)
                p.disconnect()
            except Exception as e:
                print(f'Error {e} in {self.location}... oh well')
       
            print(f'End loop for {self.location} and go ti sleep')
            time.sleep(300)
            print(f'Sleep done.. next round for {self.location}')

## Main script
if __name__ == '__main__':
    client = InfluxDBClient(url='http://localhost:8086')
    write_client = client.write_api(write_options=SYNCHRONOUS)
    config = configparser.ConfigParser()
    config.read('./config.ini')

    sections = config.sections()
    print(f'Sections in config {len(sections)}')
    threads = []
    for s in sections:
        worker = Worker(write_client, config[s]['address'], config[s]['name'])
        threads.append(worker)
        worker.start()
