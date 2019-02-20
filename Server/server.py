# For Server
import sys
import os
sys.path.append("../")
from Client import mqtt
from threading import Lock, Thread
import numpy as np
from sklearn import cluster
import datetime
import json
from dbManager import DbManager
from trainer import MiniBatchKMeansTrainer
from joblib import dump, load



class Server(object):
    def __init__(self, buffer_size = 60, batch_size = 1440, n_clusters = 9):

        # User setting
        self.user = "user_1"
        self.flora = "carnation"

        # Database manager
        self.db_manager = DbManager()

        # Async lock
        self.lock = Lock()

        # MQTT client
        self.mqtt = mqtt.Messenger(self.read_input)

        # ML Setting
        self.n_clusters = n_clusters
        self.kmeans = self._load_existing_model()
        self.batch_size = batch_size
        self.row_count = 0

        # Raw data temp storage
        self.buffer_size = buffer_size
        self.buffer = np.zeros(shape=(self.buffer_size, 4))
        self.buffer_count = 0
        self.cur_min = None             # current minute count
        self.cur_hour = None

        # Average data temp storage
        self.average = [[], [], [], []]

        # Processed data temp storage
        self.data = np.zeros(shape=(self.batch_size, 4))
        self.label = np.ndarray(shape=(self.batch_size,), dtype=str)






    def _init_optimal(self):
        return self.db_manager.get_optimal_setting(self.flora)  
    
            

    def _load_existing_model(self):
        '''load existing training model'''
        try:
            return load('model.joblib') # load existing training model
        except Exception:
            return None


    def read_input(self, topic, message):
        '''processes subscribed message'''
        if topic == self.mqtt.topic + "/history_request":   # if history data is requested
            history = self.db_manager.get_user_history(self.user, self.flora)   # obtain history from database
            if history == None:
                self.mqtt.client.publish(self.mqtt.topic + "/history", "No history")
            else:
                # send history data to mobile application
                if len(history) < 20:
                    for j in range(0, len(history)):
                        self.mqtt.client.publish(self.mqtt.topic + "/history", json.dumps(history[j]["value"]))
                else:
                    for j in range(0, 20):
                        self.mqtt.client.publish(self.mqtt.topic + "/history", json.dumps(history[j]["value"]))

            
        elif topic == self.mqtt.topic + "/raw_data":    # if raw data comes from device
            corrupted_data = False
            try:
                # try to parse the json data to see whether there is error
                co2 = message["co2"]
                organic = message["organic"]
                humidity = message["humidity"]
                temperature = message["temperature"]
                time = message["time"]
            except KeyError:
                corrupted_data = True   # if there is error, there is no further processing
            if not corrupted_data:
                date_time = datetime.datetime.strptime(message["time"], "%Y-%m-%d %H:%M:%S")    # parse time stamp
                if self.cur_min == None:
                    self.cur_min = date_time.minute
                    self.cur_hour = date_time.hour
                if self.cur_min == date_time.minute:
                    # if time stamp has not progressed into a new minute
                    self.lock.acquire()
                    try:
                        # store input data into buffer
                        self.update_buffer(co2, organic, humidity, temperature)
                        self.buffer_count = self.buffer_count + 1
                    except Exception as e:
                        print(e)
                    finally:
                        self.lock.release()
                else:
                    # if a new minute has come
                    self.lock.acquire()
                    try:
                        check_valid = self.last_nonzero(self.buffer, axis = 0, invalid_val = -1)    # find the length of buffered data
                        average = self.buffer[:check_valid[0]].mean(axis = 0)   # compute average from buffered data
                        msg_dict = {
                            "co2": co2,
                            "organic": organic,
                            "humidity": humidity,
                            "temperature": temperature,
                            "time": time
                        }
                        self.average[0].append(co2)
                        self.average[1].append(organic)
                        self.average[2].append(humidity)
                        self.average[3].append(temperature)
                        self.average.append(msg_dict)
                        self.mqtt.client.publish(self.mqtt.topic + "/average", json.dumps(msg_dict))    # send average data to mobile device for display
                        self.update_data(average, date_time)

                        # actual_implementation
                        if self.cur_hour != date_time.hour:
                            # if a new hour has come, averaged history is stored to database
                            self.write_to_database(date_time)

                    except Exception as e:
                        print (e)
                    finally:

                        # clear buffer 
                        self.row_count = self.row_count + 1
                        self.buffer_count = 0
                        self.buffer.fill(0)
                        self.cur_min = date_time.minute
                        self.cur_hour = date_time.hour
                        self.lock.release()

                    if self.row_count >= self.batch_size:
                        # if
                        self.row_count = 0
                        thread = Thread(target=self.train)
                        thread.run()
                    
    def write_to_database(self, date_time):
        try:
            history = self.db_manager.get_user_history(self.user, self.flora)
        except Exception:
            history = []
        entry = {
            "co2": round(sum(self.average[0]) // len(self.average[0]), 0),
            "organic": round(sum(self.average[1]) // len(self.average[1]), 0),
            "humidity": round(sum(self.average[2]) / len(self.average[2]), 1),
            "temperature": round(sum(self.average[3]) / len(self.average[3]), 1),
            "time": date_time.strftime("%Y-%m-%d %H"), 
        }
        update = {
            "value": entry
        }
        history.insert(0, update)
        self.db_manager.write_user_history(self.user, self.flora, history)

    def update_buffer(self, co2, organic, humidity, temperature):
        '''update buffered data for per-second readings'''
        self.buffer[self.buffer_count, 0] = co2
        self.buffer[self.buffer_count, 1] = organic
        self.buffer[self.buffer_count, 2] = humidity
        self.buffer[self.buffer_count, 3] = temperature

    def update_data(self, data, date_time):
        '''update average of readings per minute to prepare for classification'''
        self.data[self.row_count, 0] = data[0]
        self.data[self.row_count, 1] = data[1]
        self.data[self.row_count, 2] = data[2]
        self.data[self.row_count, 3] = data[3]
        self.label[self.row_count] = date_time.strftime("%Y-%m-%d %H:%M")

    def last_nonzero(self, arr, axis = 0, invalid_val = -1):
        '''find the index of the last nonzero element in nparray for computation of average'''
        mask = arr != 0
        val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis = axis) - 1
        return np.where(mask.any(axis=axis), val, invalid_val)

    def start_server(self):
        self.mqtt.client_init()
        self.mqtt.run()


    def train(self):
        self.lock.acquire()
        try:
            raw = self.data.copy()
        finally:
            self.lock.release()
        if self.kmeans == None:
            optimal = self._init_optimal()
            if optimal == None:
                self.kmeans = MiniBatchKMeansTrainer(n_clusters=self.n_clusters,
                    resolution=2, batch_size=self.batch_size)
        self.kmeans.partial_fit(raw)
        # self.kmeans.run_test_cycle()          # used for demo only

def main():
    server = Server(batch_size=1440)
    #server.start_server()

    # For test data generation
    server.flora = "parimulas"
    import random
    date_time = datetime.datetime(year = 2018, month = 7, day = 23, hour = 15)
    for i in range(40):
        for j in range(2):
            server.average[0].append(random.randint(400, 600))
            server.average[1].append(random.randint(0, 100))
            server.average[2].append(random.uniform(40, 70))
            server.average[3].append(random.uniform(-2, 6))
        date_time = date_time - datetime.timedelta(hours = 1)
        server.write_to_database(date_time)
    

if __name__ == "__main__":
    main()