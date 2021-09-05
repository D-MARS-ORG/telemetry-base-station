import datetime
import json
import logging
import logging.handlers
import pyrebase
import time
import yaml

# logging configuration
LOG_FILENAME = 'format.log'

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
with open(r'firebase_config.yml') as file:
    firebase_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'basestation_config.yml') as file:
    basestation_config = yaml.load(file, Loader=yaml.FullLoader)

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

def format_firebase():
  logging.debug('Deleting data in Firebase...')

  # Create using push
  # We are going to use this option as each send must have a unique ID.
  root_name = basestation_config['root_name']
  environment = basestation_config['environment']
  version = basestation_config['version']
  data = 'data'

  db.child(root_name) \
    .child(environment) \
    .child(version) \
    .child(data) \
    .remove(user['idToken'])

format_firebase()