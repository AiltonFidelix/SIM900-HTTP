from sim900 import SIM900
from random import randint
from json import dumps

usb = '/dev/ttyUSB0'
baud = 9600

apn = 'www.apn.com'
url = '0.0.0.0:0000/api'

data = {"device": 'sim900', "data": randint(1000, 9000)}

sim900 = SIM900(port=usb, baudrate=baud)

if sim900.port_open():
    print('Serial port opened.')
else:
    print('Serial port error.')

if sim900.is_connected():
    print('SIM900 is connected.')
else:
    print('SIM900 not found.')


print(f'Signal quality is {sim900.get_signal_quality()}.')

if sim900.set_gprs(apn=apn):
    print('GPRS mode setted.')
else:
    print('Fail to set GPRS mode.')

if sim900.post_data(dumps(data), url):
    print('HTTP POST success.')
else:
    print('HTTP POST error.')

print(sim900.get_data(url))

# print(sim900.get_date())
# print(sim900.get_hour())

sim900.port_close()
