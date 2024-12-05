import logging
import os
from uuid import uuid4
import requests

from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
from confluent_kafka import KafkaException

import logging_config
from utils import delivery_report
from admin import Admin
from producer import ProducerClass


class JsonProducer(ProducerClass):
    def __init__(
        self,
        bootstrap_server,
        topic,
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
        self.string_serializer = StringSerializer("utf-8")

    def send_message(self, key=None, value=None):
        try:
            byte_value = (
                self.string_serializer(value) if value else None
            )
            self.producer.produce(
                topic=self.topic,
                key=self.string_serializer(str(key)),
                value=byte_value,
                headers={"correlation_id": str(uuid4())},
                on_delivery=delivery_report,
            )
            logging.info("Message successfully produced by the producer")
        except KafkaException as e:
            kafka_error = e.args[0]
            if kafka_error.MSG_SIZE_TOO_LARGE:
                logging.error(
                    f"{e} , Current message size is {len(value) / (1024 * 1024)} MB"
                )
        except Exception as e:
            logging.error(f"Error while sending message: {e}")


def setting_up():
    path = os.path.dirname(os.path.abspath(__file__))

    logging_config.configure_logging()
    bootstrap_servers = "localhost:9092"
    topic = "flights_json"

    # Create Topic
    admin = Admin(bootstrap_servers)
    admin.create_topic(topic, 2)  # second parameter is for number of partitions

    # Produce messages
    producer = JsonProducer(
        bootstrap_servers,
        topic,
        compression_type="snappy",
        message_size=3 * 1024 * 1024,
        batch_size=10_00_00,  # in bytes, 1 MB
        waiting_time=10_000,  # in milliseconds, 10 seconds
    )
    return producer


if __name__ == "__main__":
    producer = setting_up()

    access_key = os.getenv("AS_API_KEY")
    if access_key is None:
        raise ValueError("Missing environment variable: 'AS_API_KEY'")

    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": access_key,
        "dep_country": "United Kingdom",
        "flight_status": "landed",
        "limit": 5,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    topic = "flights_json"

    for flight in data["data"]:
        flight_date = flight.get("flight_date", "") or ""
        flight_number = (flight.get("flight", {}) or {}).get("number", "") or ""
        departure_scheduled = (flight.get("departure", {}) or {}).get("scheduled", "") or ""

        flight_id = f"{flight_date}_{flight_number}_{departure_scheduled}"
        key = {"flight_id": flight_id}

        if flight["flight"].get("codeshared") is None:
            flight["flight"]["codeshared"] = {}

        if "departure" in flight and "delay" in flight["departure"]:
            flight["departure"]["delay"] = str(flight["departure"]["delay"]) if flight["departure"]["delay"] is not None else None

        if "arrival" in flight and "delay" in flight["arrival"]:
            flight["arrival"]["delay"] = str(flight["arrival"]["delay"]) if flight["arrival"]["delay"] is not None else None

        try:
            producer.send_message(key=key, value=flight)
        except Exception as e:
            print(f"Error message: {e}")
        producer.commit()
