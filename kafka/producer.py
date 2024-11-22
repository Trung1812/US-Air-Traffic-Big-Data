import os
import requests
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

import sys
import argparse
import time
from time import sleep
from typing import Dict
from kafka import KafkaAdminClient
from kafka.admin.new_partitions import NewPartitions

from settings import API_KEY, PRODUCE_TOPIC_FLIGHTS_REQUEST

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

def call_back(err, msg):
    """Return status for the message"""
    if err is not None:
        print("Delivery failed for record {}: {}".format(msg.key(), err))
        return
    print('Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))
    

INPUT_DATA_PATH = './resources/rides1.csv' #CHANGE TO ACTUAL VALUE
BOOTSTRAP_SERVERS = ['35.220.200.137:9092', ]  #CHANGE TO ACTUAL VALUE

# Define producer configuration
producer_config = {
    'bootstrap.servers': '172.23.0.5:9092',
    'schema.registry.url': 'http://localhost:8081'
}

class AviationStackProducer:
    def __init__(self, prop):
        value_schema = avro.load('flight-value.avsc')  # Update with your schema file path
        key_schema = avro.load('key_schema.avsc')
        self.producer = AvroProducer(prop, 
                                     default_key_schema=key_schema, 
                                     default_value_schema=value_schema)
        
    @staticmethod
    def read_records(limit: int=10, access_key=API_KEY):
        url = "http://api.aviationstack.com/v1/flights"

        # Define the query parameters
        params = {
            "access_key": access_key,
            #"dep_iata": "LHR",  # Filter flights departing from London Heathrow
            # OR
            # "arr_iata": "LGW",  # Filter flights arriving at London Gatwick
            "dep_country": "United Kingdom",  # Filter by departing country
            "flight_status": 'landed',
            "limit": limit,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception if the request failed
        data = response.json()

        messages = {}

        for flight in data['data']:
            # Generate a unique id for the flight
            flight_date = flight.get('flight_date', '') or ''
            flight_number = (flight.get('flight', {}) or {}).get('number', '') or ''
            departure_scheduled = (flight.get('departure', {}) or {}).get('scheduled', '') or ''

            flight_id = flight_date + '_' + flight_number + '_' + departure_scheduled
            flight['id'] = flight_id

            # Check if 'codeshared' field is None and if so, replace it with an empty dictionary
            if flight['flight'].get('codeshared') is None:
                flight['flight']['codeshared'] = {}

            # 'delay' is a field in 'departure', convert it to string if it exists
            if 'departure' in flight and 'delay' in flight['departure']:
                flight['departure']['delay'] = str(flight['departure']['delay']) if flight['departure']['delay'] is not None else None
            messages[flight_id] = flight
        
        return messages

    def publish(self, records: dict, sleep_time: float = 0.5):
        topic = "flights"
        
        for flight_id, flight in records.items():
            try:
            
                self.producer.produce(topic=topic, key=flight_id, value=flight)
                print(f"Producing record for <key: {flight_id}, value: {flight}> \
                      at offset {records.get().offset}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Exception while producing record - {flight}: {e}") 

            sleep(sleep_time)

        self.producer.flush()
        print("Data sent to Kafka")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', type=float, default=0.5, help='time interval between each message')
    args = parser.parse_args(sys.argv[1:])

    try:
        client = KafkaAdminClient(bootstrap_servers='localhost:9092') #CHANGE THIS TO ACTUAL VALUE LATER

        rsp = client.create_partitions({
            PRODUCE_TOPIC_FLIGHTS_REQUEST: NewPartitions(4)
        })
        print(rsp)
    except Exception as e:
        print(e)
        pass

    config = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'key_serializer': lambda x: str(x).encode('utf-8'),
        'value_serializer': lambda x: x.encode('utf-8'),
        'acks': 'all',
    }

    producer = AviationStackProducer(prop=config)
    ride_records = producer.read_records(limit=5)
    # print(ride_records)
    print(f"Producing records to topic: {PRODUCE_TOPIC_FLIGHTS_REQUEST}")

    start_time = time.time()
    producer.publish(records=ride_records, sleep_time=args.time)
    end_time = time.time()
    print(f"Producing records took: {end_time - start_time} seconds")