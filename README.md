# IoT-Projekt: Zutrittskontrolle Serverraum

Dieses Projekt ist ein smartes Zutrittssystem mit RFID, ESP32, Node-RED und SQL-Datenbank auf einem Hetzner-Server.

## Funktionen
- RFID-Zugangskontrolle
- MQTT-Kommunikation mit Node-RED
- Web-Dashboard zur Verwaltung
- Speicherung aller Zugriffe und Klimadaten in MariaDB

## Verwendete Komponenten
- ESP32
- MFRC522 RFID
- Relais
- AHT10 Sensor
- ILI9341 Display

## Serverdienste
- Node-RED (Port 1880)
- MariaDB
- Mosquitto MQTT (Port 1883)

## Node-RED Flow
→ siehe `flows.json`

## Aufbau & Code
→ siehe Python-Dateien im Repo
