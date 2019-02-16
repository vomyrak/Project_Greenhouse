# For Server
import sys
import os
sys.path.insert(0, "../")
from Client import mqtt
from threading import Lock, Thread
import numpy as np
from sklearn import cluster
os.chdir("../Client")
import datetime
import json
from dbMananger import DbManager
from trainer import MiniBatchKMeansTrainer
from joblib import dump, load



class Server(object):
    def __init__(self, thresh_file = None, buffer_size = 60, batch_size = 1440, n_clusters = 9):
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.mqtt = mqtt.Messenger(self.read_input)
        self.data = np.zeros(shape=(self.batch_size, 4))
        self.label = np.ndarray(shape=(self.batch_size,), dtype=str)
        self.threshold = self._init_threshold(thresh_file)
        self.row_count = 0
        self.lock = Lock()
        self.kmeans = self._load_existing_model()
        self.buffer = np.zeros(shape=(self.buffer_size, 4))
        self.buffer_count = 0
        self.cur_min = None
        self.n_clusters = n_clusters
        self.db_manager = DbManager()

    def _init_threshold(self, thresh_file):
        if thresh_file == None:
            return np.zeros(shape=(2, 4))
        else:
            pass

    def _load_existing_model(self):
        try:
            return load('model.joblib')
        except Exception:
            return None


    def read_input(self, topic, message):
        if topic != self.mqtt.topic + "/average":
            self.lock.acquire()
            corrupted_data = False
            try:
                co2 = message["co2"]
                organic = message["organic"]
                humidity = message["humidity"]
                temperature = message["temperature"]
                time = message["time"]

            finally:
                self.lock.release()
            if not corrupted_data:
                date_time = datetime.datetime.strptime(message["time"], "%Y-%m-%d %H:%M:%S")
                if self.cur_min == None:
                    self.cur_min = date_time.minute
                if self.cur_min == date_time.minute:
                    self.lock.acquire()
                    try:
                        self.update_buffer(co2, organic, humidity, temperature)
                        self.buffer_count = self.buffer_count + 1
                    except Exception as e:
                        print(e)
                    finally:
                        self.lock.release()
                else:
                    self.lock.acquire()
                    try:
                        check_valid = self.last_nonzero(self.buffer, axis = 0, invalid_val = -1)
                        average = self.buffer[:check_valid[0]].mean(axis = 0)
                        msg_string = {
                            "co2": co2,
                            "organic": organic,
                            "humidity": humidity,
                            "temperature": temperature,
                            "time": time
                        }
                        self.mqtt.client.publish(self.mqtt.topic + "/average", json.dumps(msg_string))
                        self.update_data(average, date_time)

                    except Exception as e:
                        print (e)
                    finally:
                        self.row_count = self.row_count + 1
                        self.buffer_count = 0
                        self.buffer.fill(0)
                        self.cur_min = date_time.minute
                        self.lock.release()

                    '''
                    if self.row_count >= self.batch_size:
                        self.row_count = 0
                    '''
                    thread = Thread(target=self.train)
                    thread.run()
                    


    def update_buffer(self, co2, organic, humidity, temperature):
        self.buffer[self.buffer_count, 0] = co2
        self.buffer[self.buffer_count, 1] = organic
        self.buffer[self.buffer_count, 2] = humidity
        self.buffer[self.buffer_count, 3] = temperature

    def update_data(self, data, date_time):
        self.data[self.row_count, 0] = data[0]
        self.data[self.row_count, 1] = data[1]
        self.data[self.row_count, 2] = data[2]
        self.data[self.row_count, 3] = data[3]
        self.label[self.row_count] = date_time.strftime("%Y-%m-%d %H:%M")

    def last_nonzero(self, arr, axis = 0, invalid_val = -1):
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
            self.kmeans = MiniBatchKMeansTrainer(raw, n_clusters=self.n_clusters, resolution=2)
            #self.kmeans.partial_fit_new()
            #self.kmeans.plot_decision_regions()
            #dump(self.kmeans.kmeans, 'test.joblib')
            self.kmeans.run_test_cycle()
        else:
            self.kmeans.run_test_cycle()

        #self.kmeans.plot_decision_regions()








def main():
    server = Server(batch_size=1440)
    server.start_server()



if __name__ == "__main__":
    main()