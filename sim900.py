from time import sleep
import serial
import re as regex


class SIM900:

    def __init__(self, port, baudrate):
        """Initialize SIM900 parameters"""
        self.__port = port
        self.__baudrate = baudrate
        self.__sim900 = serial.Serial(
            port=self.__port, baudrate=self.__baudrate)
        self.__response_ok = regex.compile(r'\bOK\b')
        self.__http_response = regex.compile(r'(?:\+HTTPACTION\:1\,(\d{3})\,)')
        self.__http_data = regex.compile(r'\{.+\}')
        self.__date = regex.compile(r'(?:\"(\d{2}\/\d{1,2}\/\d{1,2})\,)')
        self.__hour = regex.compile(r'(?:\,(\d{1,2}\:\d{1,2}\:\d{1,2})\-)')
        self.__signal = regex.compile(r'(?:\b(\d{1,2})\,)')

    def port_open(self):
        """Open serial port"""
        try:
            self.__sim900.open()
            return True
        except serial.SerialException as E:
            print(str(E))
            return False

    def port_close(self):
        """Close serial port"""
        self.__sim900.close()

    def is_connected(self):
        """Verify if sim900 is connected"""
        for i in range(10):
            self.__sim900.write(b'AT\r')
            sleep(1)
            response = self.__sim900.read_all().decode('utf8')
            if self.__response_ok.findall(response):
                return True
        return False

    def set_gprs(self, apn):
        """Set GPRS mode"""
        sleep(2)
        self.__sim900.write(b'AT+SAPBR=0,1\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if not self.__response_ok.findall(response):
            return False

        self.__sim900.write(b'AT+SAPBR=3,1,"CONTYPE","GPRS"\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if not self.__response_ok.findall(response):
            return False

        self.__sim900.write(str.encode(f'AT+SAPBR=3,1,"APN","{apn}"\r'))
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if not self.__response_ok.findall(response):
            return False

        self.__sim900.write(b'AT+SAPBR=1,1\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if not self.__response_ok.findall(response):
            return False
        return True

    def post_data(self, data, url):
        """Send HTTP POST"""
        sleep(1)
        self.__sim900.write(b'AT+HTTPINIT\r')
        sleep(1)
        self.__sim900.write(b'AT+HTTPPARA="CID",1\r')
        sleep(1)
        self.__sim900.write(str.encode(f'AT+HTTPPARA="URL","{url}"\r'))
        sleep(1)
        self.__sim900.write(b'AT+HTTPPARA="CONTENT","application/json"\r')
        sleep(1)
        self.__sim900.write(str.encode(f'AT+HTTPDATA={len(data)},10000\r'))
        sleep(1)
        self.__sim900.write(str.encode(data))
        sleep(1)
        self.__sim900.write(b'AT+HTTPACTION=1\r')
        sleep(0.5)
        self.__sim900.write(b'AT+HTTPREAD\r')
        sleep(1)
        self.__sim900.write(b'AT+HTTPTERM\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if self.__http_response.findall(response)[0] == '200':
            return True
        return False

    def get_data(self, url):
        """Send HTTP GET"""
        self.__sim900.write(b'AT+HTTPINIT\r')
        sleep(1)
        self.__sim900.write(b'AT+HTTPPARA="CID",1\r')
        sleep(1)
        self.__sim900.write(str.encode(f'AT+HTTPPARA="URL","{url}"\r'))
        sleep(1)
        self.__sim900.write(b'AT+HTTPACTION=0\r')
        sleep(2)
        self.__sim900.write(b'AT+HTTPREAD\r')
        sleep(2)
        self.__sim900.write(b'AT+HTTPTERM\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        return self.__http_data.findall(response)[0]

    def get_date(self):
        """Return current __date"""
        response = self.__timestamp()
        if response:
            return self.__date.findall(response)[0]
        return False

    def get_hour(self):
        """Return current time"""
        response = self.__timestamp()
        if response:
            return self.__hour.findall(response)[0]
        return False

    def __timestamp(self):
        """Return current time"""
        self.__sim900.write(b'AT+CCLK?\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if self.__response_ok.search(response):
            return response
        return False

    def get_signal_quality(self):
        """SIM900 signal quality"""
        self.__sim900.write(b'AT+CSQ\r')
        sleep(1)
        response = self.__sim900.read_all().decode('utf8')
        if self.__response_ok.search(response):
            return int(self.__signal.findall(response)[0])
        return 0
