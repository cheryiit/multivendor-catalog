from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import sqlite3
import json
import requests
import logging

# Kafka configuration
KAFKA_BROKER_URL = 'kafka:9092'  # Use 'kafka' as the service name within Docker
TOPIC_NAME = 'vendor_requests'

DEFAULT_IMAGE = 'image.png'
logging.basicConfig(level=logging.INFO)

def get_vendor_api_url(vendor_id):
    conn = sqlite3.connect('/databases/sqlite/products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT api_url FROM vendors WHERE id = ?", (vendor_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def insert_into_sqlite(products):
    try:
        conn = sqlite3.connect('/databases/sqlite/products.db')
        cursor = conn.cursor()

        for product in products:
            cursor.execute(
                """
                INSERT OR IGNORE INTO products (id, name, description, price)
                VALUES (?, ?, ?, ?)
                """,
                (product['id'], product['title'], DEFAULT_IMAGE, product['price'])
            )
        conn.commit()
        conn.close()
        logging.info(f"Inserted {len(products)} products into SQLite")
    except Exception as e:
        logging.exception(f"Exception occurred while inserting into SQLite: {e}")
    try:
        conn = sqlite3.connect('/databases/sqlite/products.db')
        cursor = conn.cursor()

        for product in products:
            cursor.execute(
                """
                INSERT OR IGNORE INTO products (id, name, description, price)
                VALUES (?, ?, ?, ?)
                """,
                (product['id'], product['title'], DEFAULT_IMAGE, product['price'])
            )
        conn.commit()
        conn.close()
        logging.info(f"Inserted {len(products)} products into SQLite")
    except Exception as e:
        logging.exception(f"Exception occurred while inserting into SQLite: {e}")
    conn = sqlite3.connect('/databases/sqlite/products.db')
    cursor = conn.cursor()

    for product in products:
        cursor.execute(
            """
            INSERT OR IGNORE INTO products (id, name, description, price)
            VALUES (?, ?, ?, ?)
            """,
            (product['id'], product['title'], DEFAULT_IMAGE, product['price'])
        )
    conn.commit()
    conn.close()

def insert_into_products_vendors(products, vendor_id):
    conn = sqlite3.connect('/databases/sqlite/products.db')
    cursor = conn.cursor()

    for product in products:
        cursor.execute(
            """
            INSERT OR IGNORE INTO products_vendors (product_id, vendor_id)
            VALUES (?, ?)
            """,
            (product['id'], vendor_id)
        )
    conn.commit()
    conn.close()

def process_message(message):
    try:
        logging.info(f"Received message: {message}")
        data = json.loads(message)
        vendor_id = data.get('vendor_id')

        api_url = get_vendor_api_url(vendor_id)
        logging.info(f"Fetching data from API URL: {api_url}")
        if api_url:
            response = requests.get(api_url)
            logging.info(f"API response status: {response.status_code}")
            if response.status_code == 200:
                products = response.json().get('products', [])
                logging.info(f"Fetched {len(products)} products from vendor {vendor_id}")
                insert_into_sqlite(products)
                insert_into_products_vendors(products, vendor_id)
                logging.info(f"Inserted products into SQLite for vendor {vendor_id}")
            else:
                logging.error(f"Failed to fetch data from vendor {vendor_id}, status code: {response.status_code}")
        else:
            logging.error(f"Vendor with ID {vendor_id} not found")
    except Exception as e:
        logging.exception(f"Exception occurred while processing message: {e}")
    data = json.loads(message)
    vendor_id = data.get('vendor_id')

    api_url = get_vendor_api_url(vendor_id)
    if api_url:
        response = requests.get(api_url)
        if response.status_code == 200:
            products = response.json().get('products', [])
            insert_into_sqlite(products)
            insert_into_products_vendors(products, vendor_id)
            print(f"Fetched and inserted products from vendor {vendor_id}")
        else:
            print(f"Failed to fetch data from vendor {vendor_id}")
    else:
        print(f"Vendor with ID {vendor_id} not found")

def flink_job():
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

    kafka_stream = env.add_source(kafka_consumer)

    # Process each message from Kafka
    kafka_stream.map(process_message)

    env.execute("Flink Vendor Data Fetch Job")

if __name__ == '__main__':
    flink_job()
