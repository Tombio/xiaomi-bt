# Xiaomi Mi Temperature and Humidity Monitor 2 reader

This is codebase for running central service for reading temperature and humidity data from [Xiaomi Mi](https://www.verkkokauppa.com/fi/product/649489/Xiaomi-Mi-Temperature-and-Humidity-Monitor-2-lampo-ja-kosteu) devices.

Device out of the box does provide BT notifications nor is the Mac Address anywhere on the packaging, so we need to first find the MAC, the tinker with the device a bit before we can configure it.

The system has been developed using 

`Raspberry Pi 4 Model B Rev 1.2` 

running 

`Linux version 5.10.103-v7l+ (dom@buildbot) (arm-linux-gnueabihf-gcc-8 (Ubuntu/Linaro 8.4.0-3ubuntu1) 8.4.0, GNU ld (GNU Binutils for Ubuntu) 2.34) #1529 SMP Tue Mar 8 12:24:00 GMT 2022`

### Read available BT devices

```
sudo hcitool lescan
```

Look for device called `LYWSD03MMC`

```
A4:C1:38:00:00:00 LYWSD03MMC
A4:C1:38:00:00:01 LYWSD03MMC
A4:C1:38:00:00:02 LYWSD03MMC
````

### Connect to found MAC address:

```
gatttool -I -b A4:C1:38:00:00:00
```

### inside gattool run:

```
connect
primary (to list the services)
char-write-req 0x0038 0100
```

Reqister 0x0038 is by default at value 0000. Once the bit is shifted, it'll start sending notifications every 15 seconds.


## Setup config.ini

Note the MAC address of the desired device. Make a copy of the config.template.ini as config.ini and fill in section for each sensor unit

```
[FancySpace]
floor = 2
name = Fancy space
address = A4:C1:38:00:00:00
```

## Setup InfluxDB
Follow [instructions for your system](https://docs.influxdata.com/influxdb/v1.8/introduction/install/)

Currently the code expects no authentication for local Influx