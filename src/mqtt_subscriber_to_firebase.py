import datetime
import json
import paho.mqtt.client as mqtt
import pyrebase
import time
import yaml

# read configurations

with open(r'firebase_config.yml') as file:
    firebase_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'basestation_config.yml') as file:
    basestation_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'mqtt_config.yml') as file:
    mqtt_config = yaml.load(file, Loader=yaml.FullLoader)

pyrebase_config = {
  "apiKey": firebase_config['api_key'],
  "authDomain": firebase_config['auth_domain'],
  "databaseURL": firebase_config['database_url'],
  "storageBucket": firebase_config['storage_bucket'],
  "serviceAccount": firebase_config['service_account']
}

node_ids_recognized = set()

# Firebase: initialize app with config
firebase = pyrebase.initialize_app(pyrebase_config)

# Firebase: authenticate a user
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(firebase_config['email'], firebase_config['password'])

db = firebase.database()

# need to refresh the firebase token every hour
token_refresh_counter = 0

def handle_token_refresh():
  global token_refresh_counter
  global user
  token_refresh_counter += 1
  if token_refresh_counter % 50 == 0:
    user = auth.refresh(user['refreshToken'])

def send_metadata_to_firebase(message):
  root_name = basestation_config['root_name']
  environment = basestation_config['environment']
  version = basestation_config['version']
  node_id = message['node_id']
  metadata = 'metadata'

  metadata_message  = {
    "base-station-id": basestation_config['base_station_id'],
    "source-id": basestation_config['source_id'],
    "element": basestation_config['element'],
    "location": message['location']
  }

  db.child(root_name) \
    .child(environment) \
    .child(version) \
    .child(metadata) \
    .child(node_id) \
    .set(metadata_message, user['idToken'])
  

def send_data_to_firebase(message):
  print("Sending event to Firebase...", flush=True)

  if message['node_id'] not in node_ids_recognized:
    send_metadata_to_firebase(message)
    node_ids_recognized.add(message['node_id'])

  # Create using push
  # We are going to use this option as each send must have a unique ID.
  root_name = basestation_config['root_name']
  environment = basestation_config['environment']
  version = basestation_config['version']
  data = 'data'

  telemetry  = {
    "node-id": message['node_id'],
    "data-type": message['data_type'],
    "measurement-unit": message['measurement_unit'],
    "timestamp": datetime.datetime.now().timestamp(),
    "value": message['value']
  }

  db.child(root_name) \
    .child(environment) \
    .child(version) \
    .child(data) \
    .push(telemetry, user['idToken'])

  handle_token_refresh()

client = mqtt.Client()
client.connect(mqtt_config['address'],mqtt_config['port'])

def on_connect(client, userdata, flags, rc):
    print("Connected to a broker!", flush=True)
    print(f"Subscribing to topic: {mqtt_config['topic']}", flush=True)
    client.subscribe(mqtt_config['topic'])

def on_message(client, userdata, message):
    decoded_message = message.payload.decode()
    print(decoded_message, flush=True)

    send_data_to_firebase(json.loads(decoded_message))

while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()