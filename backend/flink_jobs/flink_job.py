import sys
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import sqlite3
import json
import requests
import os
from backend.app.core.logger import setup_logger, log_step

logger = setup_logger('flink_job')

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
        log_step(logger, 2, f"Error fetching vendor API URL: {str(e)}")
        return None

def insert_into_sqlite(products, vendor_id):
    try:
        log_step(logger, 3, f"Inserting {len(products)} products into SQLite for vendor {vendor_id}")
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
        log_step(logger, 4, f"Successfully inserted {len(products)} products into SQLite for vendor {vendor_id}")
    except Exception as e:
        log_step(logger, 4, f"Error inserting products into SQLite: {str(e)}")

def get_size(obj, seen=None):
    """Recursively calculate size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def process_message(message):
    try:
        log_step(logger, 1, f"Processing message. Message size: {len(message)} bytes")
        data = json.loads(message)
        log_step(logger, 2, f"Parsed data size: {get_size(data)} bytes")
        
        vendor_id = data.get('vendor_id')
        log_step(logger, 3, f"Processing data for vendor_id: {vendor_id}")

        api_url = get_vendor_api_url(vendor_id)
        if not api_url:
            log_step(logger, 4, f"Vendor with ID {vendor_id} not found or has no API URL")
            return

        log_step(logger, 5, f"Fetching data from API URL: {api_url}")
        response = requests.get(api_url)
        log_step(logger, 6, f"API response size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            products = response.json().get('products', [])
            log_step(logger, 7, f"Fetched {len(products)} products from vendor {vendor_id}")
            log_step(logger, 8, f"Total size of products data: {get_size(products)} bytes")
            
            for i, product in enumerate(products[:5]):  # Log details of first 5 products
                log_step(logger, 9, f"Product {i+1} details: {json.dumps(product)[:200]}...")  # Log first 200 characters
            
            insert_into_sqlite(products, vendor_id)
        else:
            log_step(logger, 7, f"Failed to fetch data from vendor {vendor_id}, status code: {response.status_code}")
    except Exception as e:
        log_step(logger, 10, f"Exception occurred while processing message: {str(e)}")
        log_step(logger, 11, f"Full message content: {message[:1000]}...")  # Log first 1000 characters of the message

def flink_job():
    log_step(logger, 10, "Starting Flink job")
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_consumer = FlinkKafkaConsumer(
        topics=[TOPIC_NAME],
        deserialization_schema=SimpleStringSchema(),
        properties={
            'bootstrap.servers': KAFKA_BROKER_URL,
            'group.id': 'flink_consumer',
            'auto.offset.reset': 'earliest'
        }
    )

    log_step(logger, 11, f"Created Kafka consumer for topic: {TOPIC_NAME}")

    kafka_stream = env.add_source(kafka_consumer)
    kafka_stream.map(process_message)

    log_step(logger, 12, "Executing Flink Vendor Data Fetch Job")
    env.execute("Flink Vendor Data Fetch Job")

if __name__ == '__main__':
    flink_job()