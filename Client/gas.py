from smbus2 import SMBus, i2c_msg
import time
from gpiozero import DigitalInputDevice
from i2c_exceptions import *

class CCS811(object):
    def __init__(self, address = 0x5b, bus_index = 1):

        # Initialisation definitions
        self.bus = self.bus_init(bus_index)
        self.address = address

        # Register definitions
        self.STATUS = 0x00
        self.MODE = 0x01
        self.RESULT = 0x02
        self.ERROR = 0xE0
        self.APP_VERIFY = 0xF3
        self.APP_START = 0xF4
        self.RESET = 0xFF
        self.RESET_SEQUENCE = [0x11, 0xE5, 0x72, 0x8A]

        # Mode definitions
        self.MODE_0 = 0x00
        self.MODE_1 = 0x10
        self.MODE_2 = 0x20
        self.MODE_3 = 0x30
        self.MODE_4 = 0x40
        self.INTERRUPT = 0x08
        self.THRESHOLD = 0x04

        # Range definitions
        self.co2_min = 400
        self.co2_max = 8192
        self.tvoc_min = 0
        self.tvoc_max = 1187

        # Other definitions
        self.max_retrial_num = 5
        self.interrupt = DigitalInputDevice(18)
        
    def reset(self):
        self.bus.write_i2c_block_data(self.address, self.RESET, self.RESET_SEQUENCE)

    def read_status(self):
        return self.bus.read_byte_data(self.address, self.STATUS)
  
    def read_result(self):
        for attempt in range(self.max_retrial_num):
            try:
                while self.interrupt.value == True:
                    time.sleep(0.1)
                result = self.bus.read_i2c_block_data(self.address, self.RESULT, 8)
                return (result[:2], result[2:4], result[5], result[6], result[7:8])
            except OSError:
                if attempt < self.max_retrial_num - 1:
                    print("Remote I/O Error Happened")
                else:
                    self.terminate(2)

    def sensor_init(self):
        self.reset()
        status_OK = False
        for attempt in range(self.max_retrial_num):
            if status_OK == False:
                try:
                    self.bus.write_i2c_block_data(self.address, self.APP_START, [])
                    if self.read_status() & 1:
                        raise AppStartupFailureError()
                    print("Hardware startup complete")
                    
                    self.bus.write_byte_data(self.address, self.MODE, (self.MODE_1 | self.INTERRUPT))
                    if self.read_status() & 1:
                        raise ModeConfigurationFailureError()
                    print("Mode configuration successful")

                    status_OK = True
                except OSError:
                    if attempt < self.max_retrial_num - 1:
                        if self.read_status() & 1:
                            print("Remote I/O Error Happened During Initiation")
                            time.sleep(1)
                    else:
                        self.terminate(3)

    def convert_result(self):
        co2, organic, status, error, raw_data = self.read_result()
        co2 = (co2[0] << 8) + co2[1]
        organic = (organic[0] << 8) + organic[1]
        return co2, organic, status, error, raw_data

    def run(self):
        self.sensor_init()

        iteration_count = 0
        while True:
            try:
                iteration_count = iteration_count + 1
                print("This is the {}th iteration".format(iteration_count))
                self.convert_result()
                time.sleep(1)
            except Exception:
                a = 0

    def bus_init(self, bus_index):
        try:
            bus = SMBus(bus_index)
            return bus
        except Exception:
            self.terminate(1)

    def check_error(self):
        return self.bus.read_byte_data(self.address, self.ERROR)
    
    def terminate(self, error):
        if error == 1:
            input("Cannot establish bus connection")
        if error == 2:
            input("I/O error count exceeds limit")
        else:
            input("Unknown error occurred")
        exit()


def main():
    sensor = CCS811()
    sensor.run()

if __name__ == "__main__":
    main()