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
    def __init__(self,write_client,location, floor, id):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
        self.write_client = write_client
        self.LOC=location
        self.floor=floor
        self.id=id
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
        
        print("{} temperature={}".format(self.LOC,temp))
        print("{} humidity={}".format(self.LOC,humid))
        print("{} battery={}".format(self.LOC,battery))
       
        self.writeToDb("temperature", {"location": self.LOC, "floor": self.floor, "id": self.id}, {"value": temp})
        self.writeToDb("humidity", {"location": self.LOC, "floor": self.floor, "id": self.id}, {"value": humid})
        self.writeToDb("battery", {"location": self.LOC, "floor": self.floor, "id": self.id}, {"value": battery})
       
    def writeToDb(self, point, tags, fields):
        p = Point(point)
        for k in tags.keys():
            p.tag(k, tags[k])
        
        for k in fields.keys():
            p.field(k, fields[k])

        self.write_client.write(bucket="homemeasurements", org="home", record=p)
            
class Worker(threading.Thread):
    def __init__(self, write_client, address, location, floor = 0, id = 0):
        super(Worker, self).__init__()
        self.write_client = write_client
        self.address = address
        self.location = location
        self.floor = floor
        self.id = id

    def run(self):
        print(f'Start listening device in {self.location}: with address {self.address}')
    
        while True:
            print(f'start loop for {self.location}')
            try:        
                p = btle.Peripheral( )
                p.setDelegate(XiaoMiTemp(self.write_client, self.location, self.floor, self.id)) 
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
        worker = Worker(write_client, 
                        config[s]['address'], 
                        config[s]['name'], 
                        config[s]['floor'], 
                        config[s]['id'])
        threads.append(worker)
        worker.start()
