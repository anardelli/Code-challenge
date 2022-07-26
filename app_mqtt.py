import paho.mqtt.client as paho
#from paho import mqtt

from flask import Flask, jsonify, request
from http import HTTPStatus

OPENWEATHER_APP_ID="37faa6b3c472cea6f02216d4c4389925"
OPENWEATHER_CITY_ID=3470353
MQTT_SERVICE_HOST="localhost"
MQTT_SERVICE_PORT=1883
MQTT_SERVICE_TOPIC="casa"
MQTT_CLIENT_ID="service"

app = Flask(__name__)

parametros = [
    {
        'id': 1,
        'nome': 'temp_ON',
        'valor': '22'
    },
    {
        'id': 2,
        'nome': 'temp_OFF',
        'valor': '15'
    },
    {
        'id': 3,
        'nome': 'Hora_ON',
        'valor': '10:00'
    },
    {
        'id': 4,
        'nome': 'Hora_OFF',
        'valor': '18:00'
    },
    {
        'id': 5,
        'nome': 'STATUS_ON_OFF',
        'valor': 'OFF'
    },
    {
        'id': 6,
        'nome': 'COMANDO_ON_OFF',
        'valor': 'OFF'
    }
]

#################################
# setting callbacks for different events 
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


#################################


@app.route('/parametros', methods=['GET'])
def get_parametros():
    return jsonify({'data': parametros})


@app.route('/parametros/<int:param_id>', methods=['GET'])
def get_parametro(param_id):
    parametro = next((parametro for parametro in parametros if parametro['id'] == param_id), None)

    if parametro:
        return jsonify(parametro)

    return jsonify({'mensagem': 'parametro nao encontrado'}), HTTPStatus.NOT_FOUND

@app.route('/parametros/<int:param_id>', methods=['PUT'])
def update_parametro(param_id):
    parametro = next((parametro for parametro in parametros if parametro['id'] == param_id), None)

    if not parametro:
        return jsonify({'mensagem': 'parametro nao encontrado'}), HTTPStatus.NOT_FOUND

    data = request.get_json()

    parametro.update(
        {
            # 'nome': data.get('nome'),
            'valor': data.get('valor')
        }
    )
    
    client.publish(f"{MQTT_SERVICE_TOPIC}/{parametro['nome']}", payload=parametro['valor']), qos=1)

    return jsonify(parametro)


if __name__ == '__main__':
    client = paho.Client(client_id = "", clean_session=True, userdata=None, protocol=paho.MQTTv31)
    client.on_connect = on_connect

    # set username and password
    client.username_pw_set("challenge", "@challenge4M")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(host="localhost", port=1883, keepalive=60, bind_address="")

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    # subscribe to all topics by using the wildcard "#"
    client.subscribe("casa/#", qos=1)

    #publish data
    # client.publish("encyclopedia/temperature", payload="hot", qos=1)
    client.loop_start()

    app.run()
