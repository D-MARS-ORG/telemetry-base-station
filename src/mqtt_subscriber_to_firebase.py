import datetime
import json
import logging
import logging.handlers
import paho.mqtt.client as mqtt
import pyrebase
import time
import threading
import yaml

# logging configuration
LOG_FILENAME = '/opt/dmars/mqtt_subscriber_to_firebase.log'

root_logger=logging.getLogger()
root_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILENAME, 'w', 'utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
# Create the rotating file handler. Limit the size to 1000000Bytes ~ 1MB .
rotating_file_handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=1000000, backupCount=5)
# Add the handlers to the logger
root_logger.addHandler(file_handler)
root_logger.addHandler(rotating_file_handler)

# read configurations
with open(r'/opt/dmars/firebase_config.yml') as file:
    firebase_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'/opt/dmars/basestation_config.yml') as file:
    basestation_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'/opt/dmars/mqtt_config.yml') as file:
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

def handle_firebase_token_refresh():
  global user
  logging.debug('Refreshing Firebase token...')
  user = auth.refresh(user['refreshToken'])

# need to refresh the firebase token every hour
def handle_firebase_token_refresh_thread():
  logging.debug('handling scheduled firebase token refresh')
  handle_firebase_token_refresh()
  # 1800 seconds = 30 minutes
  threading.Timer(1800, handle_firebase_token_refresh_thread).start()

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
  logging.debug('Sending event to Firebase...')

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

client = mqtt.Client()
client.connect(mqtt_config['address'],mqtt_config['port'])

handle_firebase_token_refresh_thread()

def on_connect(client, userdata, flags, rc):
    logging.debug('Connected to a broker!')
    logging.debug('Subscribing to topic: %s', mqtt_config['topic'])
    client.subscribe(mqtt_config['topic'])

def on_message(client, userdata, message):
    decoded_message = message.payload.decode()
    logging.debug('%s', decoded_message)

    send_data_to_firebase(json.loads(decoded_message))

while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()