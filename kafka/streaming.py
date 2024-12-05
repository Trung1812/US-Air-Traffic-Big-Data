from pyspark.sql import SparkSession
import pyspark.sql.functions as F

import pyspark.sql.types as T
import os
from settings import JSON_SCHEMA

from pyspark.sql.types import (
    StructType, StructField, StringType, DateType, IntegerType, TimestampType
)

PROJECT_ID = 'totemic-program-442307-i9'
CONSUME_TOPIC_RIDES_CSV = 'flights'
KAFKA_ADDRESS= "localhost"
# KAFKA_BOOTSTRAP_SERVERS = f'{KAFKA_ADDRESS}:9092,{KAFKA_ADDRESS}:9093'
KAFKA_BOOTSTRAP_SERVERS = f'{KAFKA_ADDRESS}:9092'

GCP_GCS_BUCKET = "uk-airline-big-data"
GCS_STORAGE_PATH = 'gs://' + GCP_GCS_BUCKET + '/realtime2'
CHECKPOINT_PATH = 'gs://' + GCP_GCS_BUCKET + '/realtime2/checkpoint/'
CHECKPOINT_PATH_BQ = 'gs://' + GCP_GCS_BUCKET + '/realtime2/checkpoint_bq/'

def read_from_kafka(consume_topic: str):
    # Spark Streaming DataFrame, connect to Kafka topic served at host in bootrap.servers option
    df_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", consume_topic) \
        .option("startingOffsets", "latest") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .option("failOnDataLoss", "false") \
        .load()
    # .option("startingOffsets", "earliest") \
    return df_stream

def parse_schema_from_kafka_message(kafka_df, json_schema):
    """ take a Spark Streaming df and parse value col based on <schema>, 
    return streaming df cols in schema """
    assert kafka_df.isStreaming is True, "DataFrame doesn't receive streaming data"
    kafka_df = kafka_df.withColumn("value", F.expr("cast(value as string)"))
    streaming_df = kafka_df.withColumn("values_json", F.from_json(F.col("value"), json_schema)).selectExpr("key", "values_json.*")
    flight_df = streaming_df.select(
        # Flight-level fields
        "key",
        "flight_date",
        "flight_status",
        
        # Flatten 'departure' struct
        F.col("departure.airport").alias("departure_airport"),
        F.col("departure.timezone").alias("departure_timezone"),
        F.col("departure.iata").alias("departure_iata"),
        F.col("departure.icao").alias("departure_icao"),
        F.col("departure.terminal").alias("departure_terminal"),
        F.col("departure.gate").alias("departure_gate"),
        F.col("departure.delay").cast(IntegerType()).alias("departure_delay"),
        F.col("departure.scheduled").cast(TimestampType()).alias("departure_scheduled"),
        F.col("departure.estimated").cast(TimestampType()).alias("departure_estimated"),
        F.col("departure.actual").cast(TimestampType()).alias("departure_actual"),
        F.col("departure.estimated_runway").cast(TimestampType()).alias("departure_estimated_runway"),
        F.col("departure.actual_runway").cast(TimestampType()).alias("departure_actual_runway"),
        
        # Flatten 'arrival' struct
        F.col("arrival.airport").alias("arrival_airport"),
        F.col("arrival.timezone").alias("arrival_timezone"),
        F.col("arrival.iata").alias("arrival_iata"),
        F.col("arrival.icao").alias("arrival_icao"),
        F.col("arrival.terminal").alias("arrival_terminal"),
        F.col("arrival.gate").alias("arrival_gate"),
        F.col("arrival.baggage").alias("arrival_baggage"),
        F.col("arrival.delay").cast(IntegerType()).alias("arrival_delay"),
        F.col("arrival.scheduled").cast(TimestampType()).alias("arrival_scheduled"),
        F.col("arrival.estimated").cast(TimestampType()).alias("arrival_estimated"),
        F.col("arrival.actual").cast(TimestampType()).alias("arrival_actual"),
        F.col("arrival.estimated_runway").cast(TimestampType()).alias("arrival_estimated_runway"),
        F.col("arrival.actual_runway").cast(TimestampType()).alias("arrival_actual_runway"),
        
        # Flatten 'airline' struct
        F.col("airline.iata").alias("airline_id"),
        
        # Flatten 'flight' struct
        F.col("flight.number").alias("flight_number"),
        
        # Flatten 'codeshared' struct
        F.col("flight.codeshared.flight_iata").alias("codeshared_flight_id")
    )

    airline_df = streaming_df.select(
        F.col("airline.iata").alias("id"),
        F.col("airline.iata").alias("iata"),
        F.col("airline.icao").alias("icao"),
        F.col("airline.name").alias("name"),
    )

    codeshared_df = streaming_df.select(
        F.col("flight.codeshared.flight_iata").alias("id"),
        F.col("flight.codeshared.airline_iata").alias("airline_id"),
        F.col("flight.codeshared.flight_number").alias("flight_number"),
        F.col("flight.codeshared.flight_iata").alias("flight_iata"),
        F.col("flight.codeshared.flight_icao").alias("flight_icao"),
    )

    return flight_df, airline_df, codeshared_df


def create_file_write_stream(stream, storage_path, 
                             checkpoint_path='/checkpoint', 
                             trigger="5 seconds", 
                             output_mode="append", 
                             file_format="parquet"):
    write_stream = (stream
                    .writeStream
                    .format(file_format)
                    .partitionBy("PULocationID")
                    .option("path", storage_path)
                    .option("checkpointLocation", checkpoint_path)
                    .trigger(processingTime=trigger)
                    .outputMode(output_mode))

    return write_stream

def create_file_write_stream_bq(stream,  checkpoint_path='/checkpoint', trigger="5 seconds", output_mode="append"):
    write_stream = (stream
                    .writeStream
                    .format("bigquery")
                    .option("table", f"{PROJECT_ID}.realtime.rides")
                    .option("checkpointLocation", checkpoint_path)
                    .trigger(processingTime=trigger)
                    .outputMode(output_mode))

    return write_stream

if __name__=="__main__":
    os.environ['KAFKA_ADDRESS'] = KAFKA_ADDRESS
    os.environ['GCP_GCS_BUCKET'] = 'uk-airline-big-data'
    spark = (
        SparkSession 
        .builder 
        .appName("Streaming from Kafka") 
        .config("spark.streaming.stopGracefullyOnShutdown", True) 
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0')
        .config("spark.sql.shuffle.partitions", 4)
        .master("local[*]") 
        .getOrCreate()
    )
    spark.conf.set
    spark.sparkContext.setLogLevel('WARN')
    spark.streams.resetTerminated()

    df_consume_stream = read_from_kafka(consume_topic=CONSUME_TOPIC_RIDES_CSV)
    print(df_consume_stream.printSchema())

    # parse streaming data
    df_flight, df_airline, df_codeshared = parse_schema_from_kafka_message(df_consume_stream, JSON_SCHEMA)
    print(df_flight.printSchema())
    print(df_airline.printSchema())
    print(df_codeshared.printSchema())


    # Write to GCS
    write_stream_flights = create_file_write_stream(df_flight, GCS_STORAGE_PATH, checkpoint_path=CHECKPOINT_PATH)
    write_stream_airline = create_file_write_stream(df_airline, )
    write_stream.start()

    spark.streams.awaitAnyTermination()