import network
import time
import ubinascii
import machine
from umqtt.simple import MQTTClient
from machine import Pin

relais = Pin(16, Pin.OUT)
relais.value(0)

def verbinde_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WLAN wird verbunden...")
        wlan.connect("FRITZ!Repeater 3000 AX", "09390138198268033509")
        timeout = 0
        while not wlan.isconnected():
            time.sleep(1)
            timeout += 1
            if timeout > 15:
                print("WLAN-Verbindung fehlgeschlagen!")
                return False
    print("WLAN verbunden:", wlan.ifconfig())
    return True

def get_themen():
    return b"rfid/access", b"esp32/relay"

def verbinde_mqtt(callback):
    client_id = ubinascii.hexlify(machine.unique_id()).decode()
    client = MQTTClient(client_id, "138.199.227.39")
    client.set_callback(callback)
    client.connect()
    client.subscribe(get_themen()[1])
    print("MQTT verbunden und abonniert")
    return client

