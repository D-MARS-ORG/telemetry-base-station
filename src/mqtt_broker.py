import asyncio
import logging
import logging.handlers
import os
from hbmqtt.broker import Broker
import yaml

# logging configuration
LOG_FILENAME = 'mqtt_broker.log'

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

with open(r'mqtt_config.yml') as file:
    mqtt_config = yaml.load(file, Loader=yaml.FullLoader)

bind_config = f"{mqtt_config['address']}:{mqtt_config['port']}"

config = {
    'listeners' : {
        'default': {
            'type': 'tcp',
            'bind': bind_config
        }
    },
    'sys-interval': 10,
    'auth': {
            'allow-anonymous': True
    },
    'plugins': ['auth_anonymous'],
    'topic-check': {
        'enabled': True,
        'plugins': ['topic_taboo'],
    }
}

broker = Broker(config)

@asyncio.coroutine
def startBroker():
    yield from broker.start()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(startBroker())
    asyncio.get_event_loop().run_forever()