import paho.mqtt.client as paho
import json

class Messenger(object):
    def __init__(self):
        self.auth = self._load_auth()
        self.topic = "Hot_Wings/#"
        self.client = paho.Client()
        self.host = "m24.cloudmqtt.com"
        self.insecure_port = 18340
        self.ssl_port = 28340
        self.qos = 0

    def _load_auth(self):
        decoder = json.decoder.JSONDecoder()
        try:
            auth_file = decoder.decode(open("../Client/auth.json").read())
            return auth_file
        except IOError:
            print("No authentication file found, using unencrypted connection")
            return None

    def client_init(self):
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        if self.auth == None:
            self.client.connect(self.host, self.insecure_port)
        else:
            try:
                self.client.username_pw_set(self.auth["username"], self.auth["password"])
                self.client.tls_set(certfile=self.auth["cert"], keyfile=self.auth["key"])
                self.client.tls_insecure_set(False)
                self.client.connect(self.host, self.ssl_port)
            except KeyError:
                print("Authentication file corrupted, using insecure connection instead")
                self.client.connect(self.host, self.insecure_port)

        self.client.subscribe(self.topic, self.qos)
    
    def on_connect(self, mosq, obj, rc):
        print("connect rc: "+str(rc))
        self.client.publish("Hot_Wings","Python Script Test Message.")

    def on_message(self, mosq, obj, msg):
        print( "Received on topic: " + msg.topic + " Message: "+str(msg.payload) + "\n")
    
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