# -*- coding: utf-8 -*-
import time

import paho.mqtt.publish as publish
import requests

OPENWEATHER_APP_ID="37faa6b3c472cea6f02216d4c4389925"
OPENWEATHER_CITY_ID=3470353
MQTT_SERVICE_HOST="localhost"
MQTT_SERVICE_PORT=1883
MQTT_SERVICE_TOPIC="casa"
MQTT_CLIENT_ID="service"

if __name__ == "__main__":
    previous = 0

    while True:

        try:

            url = f"http://api.openweathermap.org/data/2.5/weather?id={OPENWEATHER_CITY_ID}&appid={OPENWEATHER_APP_ID}&type=accurate&units=metric"
            r = requests.get(url)
            data = r.json()
            print(data)
            temp = data['main'].get('temp')

            if int(data['dt']) >= int(previous):
                previous = int(data['dt'])
                msgs = []
                msgs.append({'topic': f"{MQTT_SERVICE_TOPIC}/{'temp'}", 'payload': str(temp)})
            else:
                print("No data from OWM.")

            last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['dt']))
            for i in range(60):
                print(f"{i:02}-{MQTT_SERVICE_HOST}:{MQTT_SERVICE_PORT} [last_update={last_update}]")
                publish.multiple(msgs, hostname=MQTT_SERVICE_HOST, port=MQTT_SERVICE_PORT, client_id=MQTT_CLIENT_ID)
                time.sleep(3)

        except Exception:
            print("An error occured:", exc_info=True)
