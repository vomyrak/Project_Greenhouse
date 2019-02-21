from smbus2 import SMBus, i2c_msg
import time
from i2c_exceptions import *

class SI7021(object):
    def __init__(self, address=0x40, bus_index = 1, delay=0.1):

        # Initialisation definitions
        self.bus = self.bus_init(bus_index)
        self.address = address

        # Register definitions
        self.HUMIDITY = 0xE5
        self.TEMPERATURE = 0xE0

        # Range definitions
        self.humid_min = 0
        self.humid_max = 100
        self.temp_min = -10
        self.temp_max = 85

        # Other definitions
        self.max_retrial_num = 5
        self.delay = delay

    def bus_init(self, bus_index):
        ''' initialise bus object '''
        try:
            bus = SMBus(bus_index)
            return bus
        except Exception:
            self.terminate(1)

    def run(self):
        ''' event loop '''
        while True:
            try:
                self.convert_result()
            except Exception:
                self.terminate(2)

    def convert_result(self):
        ''' convert result from bytes to actual value '''
        humid, temp = self.read_result()
        raw_humid = (humid[0] << 8) + humid[1]
        raw_temp = (temp[0] << 8) + temp[1]
        humidity = 125 * raw_humid / 65536 - 6
        temperature = 175.72 * raw_temp / 65536 - 46.85
        return round(humidity, 1), round(temperature, 1)

    def read_result(self):
        ''' result reading sequence '''

        # humidity
        self.bus.i2c_rdwr(
            i2c_msg.write(self.address, [self.HUMIDITY]))
        time.sleep(self.delay)
        humidity = i2c_msg.read(self.address, 2)
        self.bus.i2c_rdwr(humidity)
        time.sleep(self.delay)

        # temperature
        self.bus.i2c_rdwr(
            i2c_msg.write(self.address, [self.TEMPERATURE]))
        time.sleep(self.delay)
        temperature = i2c_msg.read(self.address, 2)
        self.bus.i2c_rdwr(temperature)
        return list(humidity), list(temperature)


    def terminate(self, error):

        # terminate in case of error
        if error == 1:
            input("Cannot establish bus connection")
        else:
            input("Unknown error occurred")
        exit()


def main():
    ''' testing script '''
    sensor = SI7021()
    sensor.run()

if __name__ == "__main__":
    main()