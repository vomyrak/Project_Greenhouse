from pymongo import MongoClient, errors
import json
import threading

class DbManager(object):
    '''Data base manager'''

    def __init__(self, config_file = "../credentials/dbconfig.json"):
        self.client = self._db_init(config_file)
        
    def _db_init(self, config_file):
        ''' start mongodb client using connection string file '''
        c_string = self._load_connection_str(config_file)
        return MongoClient(c_string)

    def _load_connection_str(self, config_file):
        ''' load connection string from file '''
        config = json.loads(open(config_file).read(), encoding="utf-8")
        try:
            return config["connectionString"]
        except KeyError:
            self.terminate(1)


    def get_optimal_setting(self, name):
        '''Get the optimal threshold setting from the database'''
        try:
            info =  self.client.greenhouse.flora.find_one({"name": name})
            return info
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return None

    def get_flora_data(self, name):
        '''Get threshold data value of a particular plant from database'''
        try:
            return self.client.greenhouse.flora.find_one({"name": name})
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return None

    def write_flora_data(self, data, flora):
        '''Update the new threshold value of a plant to database'''
        try:
            self.client.greenhouse.flora.find_and_modify({"name": flora}, {"$set": {"threshold": data}}, upsert=True)
            return 0
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return -1

    def get_user_history(self, user, flora):
        '''Get threshold data value of a particular plant from database'''
        try:
            user_info = self.client.greenhouse.user.find_one({"user": user})
            return user_info["history"][flora]
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return None

    def write_user_history(self, user, flora, history):
        ''' update new user's history '''
        try:
            self.client.greenhouse.user.find_and_modify({"user": user}, {"$set": {"history.{}".format(flora): history}}, upsert=True)
            return 0
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return -1 

    def terminate(self, error):
        ''' terminate programme on exception '''
        if error == 1:
            input("no connection string found, terminating programme")
        exit()