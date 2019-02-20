from humid_temp import SI7021
from gas import CCS811
from mqtt import Messenger
from controller import Controller
import json
from i2c_exceptions import *
import datetime


class MonitorSystem(object):
    def __init__(self, bus_index = 1):
        self.gas_sensor = CCS811()
        self.ht_sensor = SI7021()
        self.messenger = Messenger()
        self.controller = Controller()
    
    def run(self):
        """
        Infinite loop to try to read data from sensors
        Time is managed by CCS811 as it gives a reading every 1 sec
        """
        self.gas_sensor.sensor_init()
        self.messenger.client_init()
        iteration = 0
        while True:
            try:
                co2, organic, status, error, raw_data = self.gas_sensor.convert_result()
                humidity, temperature = self.ht_sensor.convert_result()
                if co2 < self.gas_sensor.co2_min or co2 > self.gas_sensor.co2_max:
                    raise I2CReadingError('CO2 reading corrupted')
                if organic < self.gas_sensor.tvoc_min or organic > self.gas_sensor.tvoc_max:
                    raise I2CReadingError('TVOC reading corrupted')
                if humidity < self.ht_sensor.humid_min  or humidity > self.ht_sensor.humid_max:
                    raise I2CReadingError('Humidity reading corrupted')
                if temperature < self.ht_sensor.temp_min or temperature > self.ht_sensor.temp_max:
                    raise I2CReadingError('Humidity reading corrupted')
                iteration = iteration + 1
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("This is iteration {}".format(iteration))
                print("Time stamp is: {}".format(time))
                print("Carbon dioxide concentration is: {} ppm".format(co2))
                print("Total organic concentration is: {} ppm".format(organic))
                print("Relative Humidity is: {} percent".format(humidity))
                print("Temperature is: {} degrees Celsius".format(temperature))
                print("\n")
                msg_string = {
                    "co2": co2,
                    "organic": organic,
                    "humidity": humidity,
                    "temperature": temperature,
                    "time": time
                }
                self.messenger.client.publish(self.messenger.topic + "/raw_data", json.dumps(msg_string))
            except ValueError as e:
                print(e)
                print("\n")

            except I2CReadingError as e:
                print(e)
                print("\n")

def main():
    monitor_system = MonitorSystem()
    monitor_system.run()


if __name__ == "__main__":
    main()