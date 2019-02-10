from humid_temp import SI7021
from gas import CCS811
from mqtt import Messenger
import json


class ControlSystem(object):
    def __init__(self, bus_index = 1):
        self.gas_sensor = CCS811()
        self.ht_sensor = SI7021()
        self.messenger = Messenger()
    
    def run(self):
        self.gas_sensor.sensor_init()
        self.messenger.client_init()
        iteration = 0
        while True:
            try:
                iteration = iteration + 1
                co2, organic, status, error, raw_data = self.gas_sensor.convert_result()
                humidity, temperature = self.ht_sensor.convert_result()
                print("This is iteration {}".format(iteration))
                print("Carbon dioxide concentration is: {} ppm".format(co2))
                print("Total organic concentration is: {} ppm".format(organic))
                print("Relative Humidity is: {} percent".format(humidity))
                print("Temperature is: {} degrees Celsius".format(temperature))
                msg_string = {}
                msg_string["co2"] = co2
                msg_string["organic"] = organic
                msg_string["humidity"] = humidity
                msg_string["temperature"] = temperature
                self.messenger.client.publish(self.messenger.topic[:-2], json.dumps(msg_string))
            except Exception:
                a = 0

def main():
    control_system = ControlSystem()
    control_system.run()


if __name__ == "__main__":
    main()