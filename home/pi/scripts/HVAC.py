import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from datetime import datetime
from pytz import timezone

InfluxUser = 'VAN'
InfluxPassword = 'jeepin'
DBName = 'HVACData'

dbclient = InfluxDBClient("127.0.0.1", 8086, InfluxUser, InfluxPassword, DBName)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("HVACData")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    ##raw message\
    msg.payload = msg.payload.decode("utf-8")
    #print(msg.payload)

    data = msg.payload.split(":")
    tz = timezone('MST')
    timestamp  = datetime.now(tz)
    if data[3] != "":
        dataPoint = [
            {
                "measurement": data[3],
                "tags": {
                    "device": data[0]
                    },
                    "time": timestamp,
                    "fields": {
                    "tempature": float(data[1]),
                    "humidity": float(data[2])
                    }
            }
        ]

        print(dataPoint)
        dbclient.write_points(dataPoint)
    else:
        print("Missing Data")


def influxdbConnect():
    print("DB Connected")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)

influxdbConnect()
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interfacedb
client.loop_forever()
