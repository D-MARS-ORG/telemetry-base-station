import logging
import anyio
import os
from distmqtt.broker import create_broker
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
    'topic-check': {
        'enabled': False
    }
}

async def broker_coroutine():
    async with create_broker(
        config=config
    ) as broker:
        while True:
            await anyio.sleep(99999)

if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO,format=formatter)
    anyio.run(broker_coroutine)
