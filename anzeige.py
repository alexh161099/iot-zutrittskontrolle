# Anzeige-Modul für das ILI9341-Display
from machine import Pin, SPI
import time
from ili9341 import ILI9341, color565

# SPI2 benutzen
spi = SPI(2, baudrate=20000000, sck=Pin(13), mosi=Pin(12))

# Display anschließen
screen = ILI9341(spi, cs=Pin(9), dc=Pin(11), rst=Pin(10), w=320, h=240, rot=1)

# Funktion zum Starten
def init():
    screen.fill(color565(255, 255, 255))

# Anzeige für OK (grün)
def zutritt_ok():
    screen.fill(color565(0, 200, 0))
    screen.text_scaled("Zutritt OK", 60, 100, color565(255, 255, 255), 3)

# Anzeige für Verweigert (rot)
def zutritt_verweigert():
    screen.fill(color565(200, 0, 0))
    screen.text_scaled("Zutritt", 80, 70, color565(255, 255, 255), 3)
    screen.text_scaled("verweigert", 50, 120, color565(255, 255, 255), 3)

# Standardanzeige (weiß, Temperatur und Uhrzeit)
def standard(temp, uhr):
    screen.fill(color565(255, 255, 255))
    screen.text_scaled("Temp: {} C".format(temp), 10, 40, color565(0, 0, 0), 2)
    screen.text_scaled("Uhr: {}".format(uhr), 10, 90, color565(0, 0, 0), 2)
    screen.text_scaled("Bitte Karte scannen...", 10, 130, color565(0, 0, 0), 2)
