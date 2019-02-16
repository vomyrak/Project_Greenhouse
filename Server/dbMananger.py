from pymongo import MongoClient, errors
import json
import threading

class DbManager(object):
    '''Data base manager'''

    def __init__(self, config_file = "dbconfig.json"):
        self.client = self._db_init(config_file)
        
    def _db_init(self, config_file):
        c_string = self._load_connection_str(config_file)
        return MongoClient(c_string)

    def _load_connection_str(self, config_file):
        config = json.loads(open(config_file).read(), encoding="utf-8")
        try:
            return config["connectionString"]
        except KeyError:
            return None

    def get_flora_data(self, name):
        '''Get threshold data value of a particular plant from database'''
        try:
            return self.client.greenhouse.flora.find_one({"name": name})
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return None

    def write_flora_data(self, data):
        '''Update the threshold value of a plant to database'''
        try:
            self.client.greenhouse.flora.insert_one(json.dumps(data))
            return 0
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            return -1
    


def main():
    dbManager = DbManager()
    a = 0


if __name__ == "__main__":
    main()