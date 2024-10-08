from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import Configuration
import sqlite3
import json
import requests
import os
from backend.app.core.logger import setup_logger, log_step

logger = setup_logger('flink_job', log_dir='/flink_jobs/logs')

# Kafka configuration
KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = 'vendor_requests'

DEFAULT_IMAGE = 'image.png'

def get_vendor_api_url(vendor_id):
    try:
        log_step(logger, 1, f"Fetching API URL for vendor {vendor_id}")
        conn = sqlite3.connect('/databases/sqlite/products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT api_url FROM vendors WHERE id = ?", (vendor_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            log_step(logger, 2, f"Found API URL for vendor {vendor_id}: {result[0]}")
            return result[0]
        else:
            log_step(logger, 2, f"No API URL found for vendor {vendor_id}")
            return None
    except Exception as e:
        log_step(logger, 3, f"Error fetching vendor API URL: {str(e)}")
        return None

def insert_into_sqlite(products, vendor_id):
    try:
        log_step(logger, 4, f"Inserting {len(products)} products into SQLite for vendor {vendor_id}")
        conn = sqlite3.connect('/databases/sqlite/products.db')
        cursor = conn.cursor()

        for product in products:
            cursor.execute(
                """
                INSERT OR REPLACE INTO products (id, name, description, price)
                VALUES (?, ?, ?, ?)
                """,
                (product['id'], product['title'], DEFAULT_IMAGE, product['price'])
            )
            cursor.execute(
                """
                INSERT OR REPLACE INTO products_vendors (product_id, vendor_id)
                VALUES (?, ?)
                """,
                (product['id'], vendor_id)
            )
        conn.commit()
        conn.close()
        log_step(logger, 5, f"Successfully inserted {len(products)} products into SQLite for vendor {vendor_id}")
    except Exception as e:
        log_step(logger, 6, f"Error inserting products into SQLite: {str(e)}")

def process_message(value):
    try:
        log_step(logger, 7, f"Processing message. Message size: {len(value)} bytes")
        data = json.loads(value)
        vendor_id = data.get('vendor_id')
        api_url = get_vendor_api_url(vendor_id)

        if not api_url:
            log_step(logger, 8, f"Vendor with ID {vendor_id} not found or has no API URL")
            return

        log_step(logger, 9, f"Fetching data from API URL: {api_url}")
        response = requests.get(api_url)

        if response.status_code == 200:
            products = response.json().get('products', [])
            insert_into_sqlite(products, vendor_id)
        else:
            log_step(logger, 10, f"API request failed with status code: {response.status_code}")

    except requests.RequestException as e:
        log_step(logger, 11, f"Error fetching data from vendor {vendor_id}: {str(e)}")
    except Exception as e:
        log_step(logger, 12, f"General error processing message: {str(e)}")

def flink_job():
    log_step(logger, 13, "Starting Flink job")
    config = Configuration()
    config.set_string(
        "pipeline.jars",
        "file:///opt/flink/lib/flink-connector-kafka-1.17.2.jar;file:///opt/flink/lib/kafka-clients-2.8.0.jar"
    )

    env = StreamExecutionEnvironment.get_execution_environment(configuration=config)

    kafka_props = {
        'bootstrap.servers': KAFKA_BROKER_URL,
        'group.id': 'flink_consumer',
        'auto.offset.reset': 'earliest'
    }

    kafka_consumer = FlinkKafkaConsumer(
        topics=TOPIC_NAME,
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    log_step(logger, 14, f"Created Kafka consumer for topic: {TOPIC_NAME}")

    kafka_stream = env.add_source(kafka_consumer)

    kafka_stream.map(process_message)

    log_step(logger, 15, "Executing Flink Vendor Data Fetch Job")
    env.execute("Flink Vendor Data Fetch Job")


if __name__ == '__main__':
    flink_job()
