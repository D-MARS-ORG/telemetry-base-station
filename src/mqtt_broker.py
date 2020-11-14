import logging
import asyncio
import os
from hbmqtt.broker import Broker
import yaml

logger = logging.getLogger(__name__)

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
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(startBroker())
    asyncio.get_event_loop().run_forever()