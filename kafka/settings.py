import pyspark.sql.types as T

BOOTSTRAP_SERVERS = ['35.220.200.137:9092', '35.220.200.137:9093',]

TOPIC_WINDOWED_FLIGHT_ID_COUNT = 'flight_counts_windowed'

PRODUCE_TOPIC_FLIGHTS_REQUEST = CONSUME_TOPIC_FLIGHTS_REQUEST = 'flight'

API_KEY = "7a261a4fd48779425e4a75783f089b68"
FLIGHT_URL = "http://api.aviationstack.com/v1/flights"

from pyspark.sql.types import (
    StructType, StructField, StringType, DateType, IntegerType, TimestampType
)

# Flights Table Schema
FLIGHT_SCHEMA = StructType([
    StructField("id", StringType(), nullable=False),
    StructField("flight_date", DateType(), nullable=True),
    StructField("flight_status", StringType(), nullable=True),
    StructField("departure_airport", StringType(), nullable=True),
    StructField("departure_timezone", StringType(), nullable=True),
    StructField("departure_iata", StringType(), nullable=True),
    StructField("departure_icao", StringType(), nullable=True),
    StructField("departure_terminal", StringType(), nullable=True),
    StructField("departure_gate", StringType(), nullable=True),
    StructField("departure_delay", IntegerType(), nullable=True),
    StructField("departure_scheduled", TimestampType(), nullable=True),
    StructField("departure_estimated", TimestampType(), nullable=True),
    StructField("departure_actual", TimestampType(), nullable=True),
    StructField("departure_estimated_runway", TimestampType(), nullable=True),
    StructField("departure_actual_runway", TimestampType(), nullable=True),
    StructField("arrival_airport", StringType(), nullable=True),
    StructField("arrival_timezone", StringType(), nullable=True),
    StructField("arrival_iata", StringType(), nullable=True),
    StructField("arrival_icao", StringType(), nullable=True),
    StructField("arrival_terminal", StringType(), nullable=True),
    StructField("arrival_gate", StringType(), nullable=True),
    StructField("arrival_baggage", StringType(), nullable=True),
    StructField("arrival_delay", IntegerType(), nullable=True),
    StructField("arrival_scheduled", TimestampType(), nullable=True),
    StructField("arrival_estimated", TimestampType(), nullable=True),
    StructField("arrival_actual", TimestampType(), nullable=True),
    StructField("arrival_estimated_runway", TimestampType(), nullable=True),
    StructField("arrival_actual_runway", TimestampType(), nullable=True),
    StructField("airline_id", StringType(), nullable=True),
    StructField("flight_number", StringType(), nullable=True),
    StructField("codeshared_flight_id", StringType(), nullable=True)
])

# Airlines Table Schema
AIRLINE_SCHEMA = StructType([
    StructField("id", StringType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("iata", StringType(), nullable=True),
    StructField("icao", StringType(), nullable=True)
])

# Flights Codeshared Table Schema
FLIGHT_CODESHARED_SCHEMA = StructType([
    StructField("id", StringType(), nullable=False),
    StructField("airline_id", StringType(), nullable=True),
    StructField("flight_number", StringType(), nullable=True),
    StructField("flight_iata", StringType(), nullable=True),
    StructField("flight_icao", StringType(), nullable=True)
])
