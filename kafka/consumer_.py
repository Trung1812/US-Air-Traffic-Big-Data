from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import os
from settings import FLIGHT_SCHEMA, AIRLINE_SCHEMA, FLIGHT_CODESHARED_SCHEMA

PROJECT_ID = 'totemic-program-442307-i9'
CONSUME_TOPIC_FLIGHTS = 'flights'
KAFKA_ADDRESS = "35.220.200.137"
KAFKA_BOOTSTRAP_SERVERS = f'{KAFKA_ADDRESS}:9092'

GCP_GCS_BUCKET = "uk-airline-big-data"
GCS_STORAGE_PATH = 'gs://' + GCP_GCS_BUCKET + '/realtime2'
CHECKPOINT_PATH = 'gs://' + GCP_GCS_BUCKET + '/realtime2/checkpoint/'
CHECKPOINT_PATH_BQ = 'gs://' + GCP_GCS_BUCKET + '/realtime2/checkpoint_bq/'


def read_from_kafka(consume_topic: str):
    """Read streaming data from Kafka topic."""
    df_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", consume_topic) \
        .option("startingOffsets", "latest") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .option("failOnDataLoss", "false") \
        .load()
    return df_stream


def parse_flight_from_kafka_message(df, schema):
    """
    Parse streaming Kafka data based on the given schema.
    """
    assert df.isStreaming is True, "DataFrame doesn't receive streaming data"

    df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # Parse the JSON data in the 'value' column
    df = df.withColumn("data", F.from_json("value", schema))
    return df.select("data.*")  # Expand the nested structure


def create_file_write_stream(stream, storage_path, checkpoint_path='/checkpoint',
                             trigger="5 seconds", output_mode="append",
                             file_format="parquet"):
    write_stream = (stream
                    .writeStream
                    .format(file_format)
                    .partitionBy("flight_date")  # Partition by a suitable column
                    .option("path", storage_path)
                    .option("checkpointLocation", checkpoint_path)
                    .trigger(processingTime=trigger)
                    .outputMode(output_mode))

    return write_stream


def create_file_write_stream_bq(stream, checkpoint_path='/checkpoint',
                                trigger="5 seconds", output_mode="append"):
    write_stream = (stream
                    .writeStream
                    .format("bigquery")
                    .option("table", f"{PROJECT_ID}.realtime.flights")
                    .option("checkpointLocation", checkpoint_path)
                    .trigger(processingTime=trigger)
                    .outputMode(output_mode))

    return write_stream


if __name__ == "__main__":
    os.environ['KAFKA_ADDRESS'] = KAFKA_ADDRESS
    os.environ['GCP_GCS_BUCKET'] = GCP_GCS_BUCKET
    spark = SparkSession.builder.appName('streaming-examples').getOrCreate()
    spark.conf.set('temporaryGcsBucket', 'dataproc-temp-asia-east2-285145462114-ku4fpzno')
    spark.sparkContext.setLogLevel('WARN')
    spark.streams.resetTerminated()

    # Read streaming data from Kafka
    df_consume_stream = read_from_kafka(consume_topic=CONSUME_TOPIC_FLIGHTS)
    print(df_consume_stream.printSchema())

    # Parse flights data using FLIGHT_SCHEMA
    df_flights = parse_flight_from_kafka_message(df_consume_stream, FLIGHT_SCHEMA)
    print(df_flights.printSchema())

    # Write to GCS
    write_stream = create_file_write_stream(df_flights, GCS_STORAGE_PATH, checkpoint_path=CHECKPOINT_PATH)

    # Write to BigQuery
    write_bq = create_file_write_stream_bq(df_flights, checkpoint_path=CHECKPOINT_PATH_BQ)

    # Start the streaming queries
    write_stream.start()
    write_bq.start()

    # Wait for any of the queries to terminate
    spark.streams.awaitAnyTermination()
