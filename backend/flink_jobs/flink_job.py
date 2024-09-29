from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import sqlite3
import json
import requests

# Kafka configuration
KAFKA_BROKER_URL = 'kafka:9092'  # Use 'kafka' as the service name within Docker
TOPIC_NAME = 'vendor_requests'

DEFAULT_IMAGE = 'image.png'

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
            'group.id': 'flink_consumer'
        }
    )

    kafka_stream = env.add_source(kafka_consumer)

    # Process each message from Kafka
    kafka_stream.map(process_message)

    env.execute("Flink Vendor Data Fetch Job")

if __name__ == '__main__':
    flink_job()
