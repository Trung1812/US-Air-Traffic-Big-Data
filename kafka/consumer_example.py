#NEED TO CHANGE THE SCHEMA AND TABLE CREATION
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

import pyspark.sql.types as T
import os
from settings import FLIGHT_SCHEMA, AIRLINE_SCHEMA, FLIGHT_CODESHARED_SCHEMA

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


def parse_ride_from_kafka_message(df, schema):
    """ take a Spark Streaming df and parse value col based on <schema>, 
    return streaming df cols in schema """
    assert df.isStreaming is True, "DataFrame doesn't receive streaming data"

    df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # split attributes to nested array in one Column
    col = F.split(df['value'], ', ')

    # expand col to multiple top-level columns
    for idx, field in enumerate(schema):
        df = df.withColumn(field.name, col.getItem(idx).cast(field.dataType))
    return df.select([field.name for field in schema])


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


if __name__ == "__main__":
    os.environ['KAFKA_ADDRESS'] = KAFKA_ADDRESS
    os.environ['GCP_GCS_BUCKET'] = 'uk-airline-big-data'
    spark = SparkSession.builder.appName('streaming-examples').getOrCreate()
    spark.conf.set('temporaryGcsBucket', 'dataproc-temp-asia-east2-285145462114-ku4fpzno')
    spark.sparkContext.setLogLevel('WARN')
    spark.streams.resetTerminated()

    # read_streaming data
    df_consume_stream = read_from_kafka(consume_topic=CONSUME_TOPIC_RIDES_CSV)
    print(df_consume_stream.printSchema())

    # parse streaming data
    df_rides = parse_ride_from_kafka_message(df_consume_stream, FLIGHT_SCHEMA)
    print(df_rides.printSchema())

    # Write to GCS
    write_stream = create_file_write_stream(df_rides, GCS_STORAGE_PATH, checkpoint_path=CHECKPOINT_PATH)
    write_bq = create_file_write_stream_bq(df_rides, checkpoint_path=CHECKPOINT_PATH_BQ)

    write_stream.start()
    write_bq.start()

    spark.streams.awaitAnyTermination()