import paho.mqtt.client as paho
import json
import threading

class Messenger(object):
    def __init__(self, method = None):
        self.auth = self._load_auth()
        self.topic = "Hot_Wings"
        self.client = paho.Client()
        self.host = "m24.cloudmqtt.com"
        self.insecure_port = 18340
        self.ssl_port = 28340
        self.qos = 2
        self.handler = method
        self.max_reconnection_num = 5
        self.cur_trial_num = 0
    
    def _load_auth(self, is_secure = True):
        """Load authentication json file"""
        try:
            if is_secure:
                auth_file = json.loads(open("../credentials/auth.json").read())
                return auth_file
            
            else:
                auth_file = json.loads(open("../credentials/insecure_auth.json").read())
                return auth_file

        except IOError:

            return None


    def client_init(self):
        """Initialise client setting"""

        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect
        
        if self.auth == None:
            print("No authentication file found, using unencrypted connection")
            self.client_insecure_init()
        else:
            try:
                self.client.username_pw_set(self.auth["username"], self.auth["password"])
                self.client.tls_set(certfile=self.auth["cert"], keyfile=self.auth["key"])
                self.client.tls_insecure_set(False)
                self.client.connect(self.host, self.ssl_port)
            except KeyError:
                print("Authentication file corrupted, using insecure connection instead" + 
                    " with default username and password")
                self.client_insecure_init()
            
        print("Connection complete")
        self.client.subscribe(self.topic + "/history_request", self.qos)
    
    def client_insecure_init(self):
        try:
            self.auth = self._load_auth(False)
            self.client.username_pw_set(self.auth["username"], self.auth["password"])
            self.client.connect(self.host, self.insecure_port)
        except KeyError:
            print("Insecure authentication file corrupted, connection failed")
            exit()

    def on_disconnect(self, client, userdata, rc):
        """
        Disconnection handler
        Tries to reconnect after disconnection
        """
        
        if rc != 0:
            print("Unexpected disconnection")
            self.cur_trial_num += 1
            if self.cur_trial_num < self.max_reconnection_num:
                self.client.reinitialise()
                self.client_init()
                self.run()

    def on_connect(self, mosq, obj, rc):
        #print("Connection complete")
        #self.client.subscribe(self.topic + "/#", self.qos)
        pass

    def on_message(self, mosq, obj, msg):
        print( "Received on topic: " + msg.topic + " Message: "+str(msg.payload) + "\n")
        message = msg.payload.decode("utf-8")
        message = json.loads(message)
        if self.handler != None:
            self.handler(msg.topic, message)

    
    
    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed OK")

    def run(self):
        rc = 0
        while rc == 0:
            rc = self.client.loop()
        print("rc: "+str(rc))


def main():
    messenger = Messenger()
    messenger.client_init()
    messenger.run()


if __name__ == "__main__":
    main()