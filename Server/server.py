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
from miscellaneous.definition import *



class Server(object):
    def __init__(self, buffer_size = 60, batch_size = 1440, n_clusters = 81):

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
        self.batch_size = batch_size
        self.row_count = 0
        self.kmeans = self._load_kmeans_model()
        self.mean_setting = self.kmeans.kmeans.cluster_centers_

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
            

    def _load_kmeans_model(self):
        '''load or initialise training model'''
        return MiniBatchKMeansTrainer(n_clusters=self.n_clusters,
                resolution=2, batch_size=self.batch_size)

    def _find_average_setting(self):
        ''' find the average of current cluster centroids '''
        return np.average(self.kmeans.kmeans.cluster_centers_, axis=0)

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
                self.check_control(co2, organic, humidity, temperature)
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
                        self.average[co2_index].append(co2)
                        self.average[organic_index].append(organic)
                        self.average[humidity_index].append(humidity)
                        self.average[temperature_index].append(temperature)
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
                        # if number of averages equal to batch size, start async training
                        self.row_count = 0
                        thread = Thread(target=self.train)
                        thread.run()
                    


    def check_control(self, co2, organic, humidity, temperature):
        ''' compare the centroid of current input readings with optimal centroid 
            and write control signal accordingly '''

        # use current input for prediction
        data = np.array([[co2, organic, humidity, temperature]])
        data = self.kmeans.kmeans.predict(data)
        decision = []
        update_required = False

        # if the indicator value of predicted centroid is different from that of optimal
        # control is needed
        for i in range(0, 4):

            if data[0, i] < self.mean_setting[i]:
                decision.append(-1)
                update_required = True
            elif data[0, i] > self.mean_setting[i]:
                decision.append(1)
                update_required = True
            else:
                decision.append(0) 

        if update_required:
            # if control is needed, notify client device for control
            self.mqtt.client.publish(self.mqtt.topic + "/control", json.dumps(decision))

    def write_to_database(self, date_time):
        ''' update history to database '''
        try:
            # try to find out whether existing history is available
            # if not, create new history object
            history = self.db_manager.get_user_history(self.user, self.flora)
        except Exception:
            history = []
        
        # format new entry
        entry = {
            "co2": round(sum(self.average[co2_index]) // len(self.average[co2_index]), 0),
            "organic": round(sum(self.average[organic_index]) // len(self.average[organic_index]), 0),
            "humidity": round(sum(self.average[humidity_index]) / len(self.average[humidity_index]), 1),
            "temperature": round(sum(self.average[temperature_index]) / len(self.average[temperature_index]), 1),
            "time": date_time.strftime("%Y-%m-%d %H"), 
        }
        update = {
            "value": entry
        }

        # insert new history to the front of past history
        history.insert(0, update)
        self.db_manager.write_user_history(self.user, self.flora, history)

    def update_buffer(self, co2, organic, humidity, temperature):
        '''update buffered data for per-second readings'''
        self.buffer[self.buffer_count, co2_index] = co2
        self.buffer[self.buffer_count, organic_index] = organic
        self.buffer[self.buffer_count, humidity_index] = humidity
        self.buffer[self.buffer_count, temperature_index] = temperature

    def update_data(self, data, date_time):
        '''update average of readings per minute to prepare for classification'''
        self.data[self.row_count, co2_index] = data[co2_index]
        self.data[self.row_count, organic_index] = data[organic_index]
        self.data[self.row_count, humidity_index] = data[humidity_index]
        self.data[self.row_count, temperature_index] = data[temperature_index]
        self.label[self.row_count] = date_time.strftime("%Y-%m-%d %H:%M")

    def last_nonzero(self, arr, axis = 0, invalid_val = -1):
        '''find the index of the last nonzero element in nparray for computation of average'''
        # masking array for non-zero contents
        mask = arr != 0 
        val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis = axis) - 1
        return np.where(mask.any(axis=axis), val, invalid_val)  # return the position of the last non_zero element

    def start_server(self):
        ''' start server '''
        self.mqtt.client_init()
        self.mqtt.run()


    def train(self):
        ''' asynchronous training '''
        self.lock.acquire()
        try:
            ''' deep copy current raw data '''
            raw = self.data.copy()
        finally:
            self.lock.release()
        self.kmeans.partial_fit(raw)
        self.mean_setting = self._find_average_setting()




def main():
    server = Server(batch_size=1440)
    server.start_server()

if __name__ == "__main__":
    main()