import logging
import os
from uuid import uuid4
import requests

from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

import logging_config as logging_config
import utils
from utils import delivery_report
from admin import Admin
from producer import ProducerClass
from schema_registry_client import SchemaClient
from confluent_kafka import KafkaException

from settings import AS_API_KEY


class AvroProducer(ProducerClass):
    def __init__(
        self,
        bootstrap_server,
        topic,
        schema_registry_client,
        schema_str,
        compression_type=None,
        message_size=None,
        batch_size=None,
        waiting_time=None,
    ):
        super().__init__(
            bootstrap_server,
            topic,
            compression_type,
            message_size,
            batch_size,
            waiting_time,
        )
        self.schema_registry_client = schema_registry_client
        self.schema_str = schema_str
        self.avro_serializer = AvroSerializer(schema_registry_client, schema_str)
        self.string_serializer = StringSerializer("utf-8")

    def send_message(self, key=None, value=None):
        try:
            if value:
                byte_value = self.avro_serializer(
                    value, SerializationContext(self.topic, MessageField.VALUE)
                )
            else:
                byte_value = None
            self.producer.produce(
                topic=self.topic,
                key=self.string_serializer(str(key)),
                value=byte_value,
                headers={"correlation_id": str(uuid4())},
                on_delivery=delivery_report,
            )
            logging.info("Message Successfully Produce by the Producer")
        except KafkaException as e:
            kafka_error = e.args[0]
            if kafka_error.MSG_SIZE_TOO_LARGE:
                logging.error(
                    f"{e} , Current Message size is {len(value) / (1024 * 1024)} MB"
                )
        except Exception as e:
            logging.error(f"Error while sending message: {e}")

def setting_up():
    # Get the directory where the current script is located
    path = os.path.dirname(os.path.abspath(__file__))

    # Load the Avro schema files for key and value
    value_schema_file = os.path.join(path,"flight-value.avsc")     # Update with your value schema file

    logging_config.configure_logging()
    schema_registry_url = "http://localhost:8081"
    bootstrap_servers = "localhost:9092"
    topic = "flights"
    schema_type = "AVRO"

    # Create Topic
    admin = Admin(bootstrap_servers)
    admin.create_topic(topic, 2)  # second parameter is for number of partitions

    with open(value_schema_file) as avro_schema_file:
        value_avro_schema = avro_schema_file.read()

    schema_client = SchemaClient(schema_registry_url, topic, value_avro_schema, schema_type)
    schema_client.set_compatibility("BACKWARD")
    schema_client.register_schema()

    # fetch schema_str from Schema Registry
    schema_str = schema_client.get_schema_str()
    # Produce messages
    producer = AvroProducer(
        bootstrap_servers,
        topic,
        schema_client.schema_registry_client,
        schema_str,
        compression_type="snappy",
        message_size=3 * 1024 * 1024,
        batch_size=10_00_00,  # in bytes, 1 MB
        waiting_time=10_000,  # in milliseconds, 10 seconds
    )
    return producer

if __name__=="__main__":
    producer = setting_up()
    #utils.load_dotenv()

    access_key = AS_API_KEY #os.getenv('access_key')
    if access_key is None:
        raise ValueError("Missing environment variable: 'access_key'")

    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": access_key,
        #"dep_iata": "LHR",  # Filter flights departing from London Heathrow
        # OR
        # "arr_iata": "LGW",  # Filter flights arriving at London Gatwick
        "dep_country": "United Kingdom",  # Filter by country
        "flight_status": 'landed',
        "limit": 5,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  
    data = response.json()

    topic = 'flights'

    for flight in data['data']:
        flight_date = flight.get('flight_date', '') or ''
        flight_number = (flight.get('flight', {}) or {}).get('number', '') or ''
        departure_scheduled = (flight.get('departure', {}) or {}).get('scheduled', '') or ''

        flight_id = flight_date + '_' + flight_number + '_' + departure_scheduled
        key = {"flight_id": flight_id}
        if flight['flight'].get('codeshared') is None:
            flight['flight']['codeshared'] = {}

        if 'departure' in flight and 'delay' in flight['departure']:
            flight['departure']['delay'] = str(flight['departure']['delay']) if flight['departure']['delay'] is not None else None

        if 'arrival' in flight and 'delay' in flight['arrival']:
            flight['arrival']['delay'] = str(flight['arrival']['delay']) if flight['arrival']['delay'] is not None else None

        try:
            producer.send_message(key=key, value=flight)
        except Exception as e:
            print(f"Error message: {e}")
        producer.commit()