# AHT10 Temperatur- und Feuchtesensor
from machine import I2C, Pin
import time

# Sensor-Adresse
adresse = 0x38

# I2C1 mit GPIO 38 (SCL) und 37 (SDA)
i2c = I2C(1, scl=Pin(38), sda=Pin(37))

# Sensor vorbereiten
def init():
    try:
        i2c.writeto(adresse, b'\xE1\x08\x00')
        time.sleep(0.25)
    except:
        print("Fehler beim Initialisieren des Sensors")

# Temperatur und Luftfeuchtigkeit auslesen
def lese():
    try:
        i2c.writeto(adresse, b'\xAC\x33\x00')
        time.sleep(0.2)
        daten = i2c.readfrom(adresse, 6)
        hum_raw = ((daten[1] << 16) | (daten[2] << 8) | daten[3]) >> 4
        temp_raw = ((daten[3] & 0x0F) << 16) | (daten[4] << 8) | daten[5]
        hum = hum_raw * 100 / 1048576.0
        temp = temp_raw * 200 / 1048576.0 - 50
        return round(temp, 1), round(hum, 1)
    except:
        print("Fehler beim Lesen vom Sensor")
        return None, None
