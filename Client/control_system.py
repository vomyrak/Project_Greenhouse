from humid_temp import SI7021
from gas import CCS811
from mqtt import Messenger
from controller import Controller
import json
from i2c_exceptions import *
import datetime
import sys
sys.path.append("../")
from miscellaneous.definition import *


class MonitorSystem(object):
    def __init__(self, bus_index = 1):
        ''' initialise all system components '''
        self.gas_sensor = CCS811()
        self.ht_sensor = SI7021()
        self.controller = Controller()
        self.messenger = Messenger(self.process_control)
    
    def process_control(self, topic, message):
        ''' control ventilation and irrigation depending on incoming control message '''
        if topic == self.messenger.topic + "/control":
            if message[co2_index] == 1:
                self.controller.ventilation_up()    # if co2 concentration too high, turn up ventilation
            elif message[co2_index] == -1:
                self.controller.ventilation_down()  # if co2 concentration too low, turn down ventilation
            if message[humidity_index] == 1:
                self.controller.irrigation_down()   # if humidity too high, turn down irrigation
            elif message[humidity_index] == -1:
                self.controller.irrigation_up()     # if humidity too low, turn up irrigation

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
                # read gas sensor result
                # since gas sensor result only returns every second, this has the effect of delay
                co2, organic, status, error, raw_data = self.gas_sensor.convert_result() 

                # start reading humidity, temperature data once gas sensor data is ready
                humidity, temperature = self.ht_sensor.convert_result()

                # detect out of range values, but number itself will not be handled here
                if co2 < self.gas_sensor.co2_min or co2 > self.gas_sensor.co2_max:
                    raise I2CReadingError('CO2 reading corrupted')
                if organic < self.gas_sensor.tvoc_min or organic > self.gas_sensor.tvoc_max:
                    raise I2CReadingError('TVOC reading corrupted')
                if humidity < self.ht_sensor.humid_min  or humidity > self.ht_sensor.humid_max:
                    raise I2CReadingError('Humidity reading corrupted')
                if temperature < self.ht_sensor.temp_min or temperature > self.ht_sensor.temp_max:
                    raise I2CReadingError('Humidity reading corrupted')
                iteration = iteration + 1

                # get current date and time
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("This is iteration {}".format(iteration))
                print("Time stamp is: {}".format(time))
                print("Carbon dioxide concentration is: {} ppm".format(co2))
                print("Total organic concentration is: {} ppm".format(organic))
                print("Relative Humidity is: {} percent".format(humidity))
                print("Temperature is: {} degrees Celsius".format(temperature))
                print("\n")


                # wraps reading to send as mqtt message
                msg_string = {
                    "co2": co2,
                    "organic": organic,
                    "humidity": humidity,
                    "temperature": temperature,
                    "time": time
                }
                self.messenger.client.publish(self.messenger.topic + "/raw_data", json.dumps(msg_string))

            # exceptions at this stage are not critical so only print message for notification
            except ValueError as e:
                print(e)
                print("\n")

            except I2CReadingError as e:
                print(e)
                print("\n")

def main():
    ''' start-up script '''
    monitor_system = MonitorSystem()
    monitor_system.run()


if __name__ == "__main__":
    main()