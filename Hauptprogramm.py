
import time
import sensor as temperatur_sensor
import rfid as rfid_modul
import anzeige
import netzwerk
import machine

# WLAN verbinden
if not netzwerk.verbinde_wlan():
    print("WLAN-Verbindung fehlgeschlagen. Neustart...")
    machine.reset()

relais_aktiv_bis = 0
zeige_standard_wieder_ab = 0
warte_auf_unlock_bis = 0
letzte_uid = None
freigabe_erfolgt = False
letzte_scan_zeit = 0

def empfange_mqtt(topic, msg):
    global relais_aktiv_bis, zeige_standard_wieder_ab, warte_auf_unlock_bis, freigabe_erfolgt
    THEMA_RFID, THEMA_RELAIS = netzwerk.get_themen()
    if topic == THEMA_RELAIS and msg == b'unlock':
        print("Unlock empfangen")
        netzwerk.relais.value(1)
        anzeige.zutritt_ok()
        relais_aktiv_bis = time.ticks_add(time.ticks_ms(), 3000)
        zeige_standard_wieder_ab = time.ticks_add(time.ticks_ms(), 3000)
        warte_auf_unlock_bis = 0
        freigabe_erfolgt = True

client = netzwerk.verbinde_mqtt(empfange_mqtt)
temperatur_sensor.init()
letzte_anzeige = 0

while True:
    client.check_msg()

    # Relais nach Zeit aus
    if relais_aktiv_bis and time.ticks_diff(relais_aktiv_bis, time.ticks_ms()) <= 0:
        netzwerk.relais.value(0)
        relais_aktiv_bis = 0
        print("Relais deaktiviert")
        letzte_uid = None

    # Nur alle 1,5s RFID prüfen
    if time.ticks_diff(time.ticks_ms(), letzte_scan_zeit) > 1500:
        uid = rfid_modul.lese_uid()
        if uid and uid != letzte_uid:
            print("Neue UID erkannt:", uid)
            letzte_uid = uid
            client.publish(netzwerk.get_themen()[0], '{{"uid": "{}"}}'.format(uid))
            warte_auf_unlock_bis = time.ticks_add(time.ticks_ms(), 2000)
            freigabe_erfolgt = False
            letzte_scan_zeit = time.ticks_ms()
        elif not uid:
            letzte_uid = None

    # Wenn kein Unlock kam
    if warte_auf_unlock_bis and time.ticks_diff(warte_auf_unlock_bis, time.ticks_ms()) <= 0:
        if not freigabe_erfolgt:
            print("Zugriff verweigert")
            anzeige.zutritt_verweigert()
            zeige_standard_wieder_ab = time.ticks_add(time.ticks_ms(), 2000)
        warte_auf_unlock_bis = 0
        letzte_uid = None
        freigabe_erfolgt = False

    # Temperaturanzeige
    if not warte_auf_unlock_bis and not zeige_standard_wieder_ab:
        if time.ticks_diff(time.ticks_ms(), letzte_anzeige) > 10000:
            temp, hum = temperatur_sensor.lese()
            if temp is not None:
                uhr = "{:02}:{:02}".format((time.localtime()[3] + 2) % 24, time.localtime()[4])
                anzeige.standard(temp, uhr)
            letzte_anzeige = time.ticks_ms()

    # Anzeige zurücksetzen
    if zeige_standard_wieder_ab and time.ticks_diff(zeige_standard_wieder_ab, time.ticks_ms()) <= 0:
        temp, hum = temperatur_sensor.lese()
        if temp is not None:
            uhr = "{:02}:{:02}".format((time.localtime()[3] + 2) % 24, time.localtime()[4])
            anzeige.standard(temp, uhr)
        zeige_standard_wieder_ab = 0


