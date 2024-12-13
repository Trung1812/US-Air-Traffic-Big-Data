import os

from utils import *
#from settings import KAFKA_ADDRESS
from json_producer import setting_up, process_data_from_api, request_us_flights
import time
import random

KAFKA_ADDRESS = "35.240.239.52:9092"
if __name__=="__main__":
    producer = setting_up(bootstrap_servers=KAFKA_ADDRESS, topic="flights")
    access_key = os.environ.get("ACCESS_KEY", "0f1f4a0ab47894952b1e301b3f928910")

    url = "http://api.aviationstack.com/v1/flights"

    dirpath = os.path.dirname(os.path.abspath(__file__))
    iata_file_path = os.path.join(dirpath, "us_airport_iata.txt")
    with open(iata_file_path, 'r') as file:
        airport_iata = [line.strip() for line in file]

    dep_iata = random.choices(airport_iata, k=1)
    arr_iata = random.sample(airport_iata, k=1)
    offset=0
    for i in range(1):
        data = request_us_flights(access_key, retries=1, dep_airports=dep_iata,
                                  arr_airports=arr_iata, limit=100,
                                  offset=offset)
        offset += 100
        print(data)
        for flight in data:
            key, value = process_data_from_api(flight)
            try:
                producer.send_message(key=key, value=value)
            except Exception as e:
                print(f"Error message: {e}")
            producer.commit()
        time.sleep(600)