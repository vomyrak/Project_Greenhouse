from smbus2 import SMBus, i2c_msg
import time

class SI7021(object):
    def __init__(self, ADDRESS=0x40, bus_index = 1, delay=0.1):
        self.bus = self.bus_init(bus_index)
        self.ADDRESS = ADDRESS
        self.max_retrial_num = 5
        self.HUMIDITY = 0xE5
        self.TEMPERATURE = 0xE0
        self.delay = delay

    def bus_init(self, bus_index):
        try:
            bus = SMBus(bus_index)
            return bus
        except Exception:
            self.terminate(1)

    def run(self):
        while True:
            try:
                self.convert_result()
            except Exception:
                a = 0

    def convert_result(self):
        humid, temp = self.read_result()
        raw_humid = (humid[0] << 8) + humid[1]
        raw_temp = (temp[0] << 8) + temp[1]
        humidity = 125 * raw_humid / 65536 - 6
        temperature = 175.72 * raw_temp / 65536 - 46.85
        return round(humidity, 2), round(temperature, 2)

    def read_result(self):
        self.bus.i2c_rdwr(
            i2c_msg.write(self.ADDRESS, [self.HUMIDITY]))
        time.sleep(self.delay)
        humidity = i2c_msg.read(self.ADDRESS, 2)
        self.bus.i2c_rdwr(humidity)
        time.sleep(self.delay)
        self.bus.i2c_rdwr(
            i2c_msg.write(self.ADDRESS, [self.TEMPERATURE]))
        time.sleep(self.delay)
        temperature = i2c_msg.read(self.ADDRESS, 2)
        self.bus.i2c_rdwr(temperature)
        return list(humidity), list(temperature)


    def terminate(self, error):
        if error == 1:
            input("Cannot establish bus connection")
        else:
            input("Unknown error occurred")
        exit()


def main():
    sensor = SI7021()
    sensor.run()

if __name__ == "__main__":
    main()