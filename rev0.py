import machine
import network
import ssl
import time
import ubinascii
import tls
import json

from simple import MQTTClient

SSID = 'Redmi10'
PASSWORD = 'shami1234'

# Step 1: Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)

    print("Connected to WiFi")

connect_wifi()

MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_CLIENT_KEY = "843e2d584270685ecd66ca6f126bce7cb48c866032b92145476381dcc4a9b641-private.pem.key"
MQTT_CLIENT_CERT = "843e2d584270685ecd66ca6f126bce7cb48c866032b92145476381dcc4a9b641-certificate.pem.crt"
MQTT_BROKER = "a3p3vavqt7h3qx-ats.iot.us-east-1.amazonaws.com"
MQTT_BROKER_CA = "AmazonRootCA1.pem"

led = machine.Pin(2, machine.Pin.OUT)
led.on()

def read_pem(file):
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        return ubinascii.a2b_base64(base64_text)

# callback function to handle received MQTT messages
def on_mqtt_msg(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()

    print(f"RX: {topic_str}\n\t{msg_str}")

    if topic_str == 'LED':
        msg_json = json.loads(msg_str)
        if msg_json.get("message") == "on":
            led.on()
        elif msg_json.get("message") == "off":
            led.off()
        elif msg_json.get("message") == "toggle":
            led.toggle()

context = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
context.load_cert_chain(read_pem(MQTT_CLIENT_CERT), read_pem(MQTT_CLIENT_KEY))
context.load_verify_locations(read_pem(MQTT_BROKER_CA))
context.verify_mode = tls.CERT_REQUIRED

mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=context,
)

print(f"Connecting to MQTT broker")
mqtt_client.set_callback(on_mqtt_msg)
mqtt_client.connect()
mqtt_client.subscribe('LED')
print("Connection established, awaiting messages")

while True:
    mqtt_client.check_msg()
