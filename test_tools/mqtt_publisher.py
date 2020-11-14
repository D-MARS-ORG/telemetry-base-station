# publisher simulator
import json
import paho.mqtt.client as mqtt
import requests
import sched
import time
import yaml

# read configurations

with open(r'../src/mqtt_config.yml') as file:
    mqtt_config = yaml.load(file, Loader=yaml.FullLoader)

with open(r'openweathermap_config.yml') as file:
    openweathermap_config = yaml.load(file, Loader=yaml.FullLoader)

client = mqtt.Client()
client.connect(mqtt_config['address'],mqtt_config['port'])


# openweathermap config
api_key = openweathermap_config['api_key']
location = openweathermap_config['location']
url = f"{openweathermap_config['url']}?q={location}&APPID={api_key}"

def convert_kelvin_to_celsius(kelvin_temperature):
    return round(kelvin_temperature - 273.15, 2)

def collect_temperature():
  response = requests.get(url).json()
  current_temperature_kelvin = response['main']['temp']
  current_temperature_celsius = convert_kelvin_to_celsius(current_temperature_kelvin)
  print("Current temperature: ", current_temperature_celsius)
  return current_temperature_celsius

# while True:
#    client.publish(mqtt_config['topic'], input('Message : '))

def send_temperature_sample():
    message  = {
        "location": "Laboratory",
        "node_id": "9ab93a61-bfad-442a-b551-5a155545bb60",
        "data_type": "Temperature",
        "measurement_unit": "Celsius",
        "value": collect_temperature()
    }
    client.publish(mqtt_config['topic'], json.dumps(message))


scheduler = sched.scheduler(time.time, time.sleep)
def schedule_send(scheduler): 
    send_temperature_sample()
    scheduler.enter(60, 1, schedule_send, (scheduler,))

scheduler.enter(60, 1, schedule_send, (scheduler,))
scheduler.run()