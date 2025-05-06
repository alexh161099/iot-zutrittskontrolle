from machine import Pin, SPI
from mfrc522 import MFRC522

# SPI initialisieren
spi_rfid = SPI(1, baudrate=1000000, polarity=0, phase=0,
               sck=Pin(18), mosi=Pin(5), miso=Pin(19))
reader = MFRC522(spi_rfid, rst=Pin(4), cs=Pin(15))

# UID lesen
def lese_uid():
    stat, tag_type = reader.request(reader.REQIDL)
    if stat == reader.OK:
        stat, uid = reader.anticoll()
        if stat == reader.OK:
            return "-".join([str(x) for x in uid])
    return None

# Bei Bedarf neu initialisieren
def reset_reader():
    reader.init()
