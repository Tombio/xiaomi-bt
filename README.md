# Xiaomi Mi Temperature and Humidity Monitor 2 reader

Read devices:
sudo hcitool lescan

Connect to found MAC address:
gatttool -I -b 00:00:00:00:00:00

inside gattool:
connect
primary
char-write-req 0x0038 0100
