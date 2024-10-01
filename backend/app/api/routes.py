from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db_connection
from core.kafka_producer import send_data_to_kafka
from core.logger import setup_logger, log_step

router = APIRouter()
logger = setup_logger('api_routes')

@router.get("/products")
def get_products(vendor_id: int = None, conn=Depends(get_db_connection)):
    log_step(logger, 1, f"Received request for products. Vendor ID: {vendor_id}")
    cursor = conn.cursor()
    if vendor_id:
        log_step(logger, 2, f"Fetching products for vendor ID: {vendor_id}")
        cursor.execute("""
            SELECT p.*
            FROM products p
            JOIN products_vendors pv ON p.id = pv.product_id
            WHERE pv.vendor_id = ?
        """, (vendor_id,))
    else:
        log_step(logger, 2, "Fetching all products")
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        log_step(logger, 3, "No products found. Initiating data fetch process.")
        if vendor_id:
            log_step(logger, 4, f"Sending Kafka message for vendor ID: {vendor_id}")
            send_data_to_kafka({'vendor_id': vendor_id})
        else:
            log_step(logger, 4, "Sending Kafka messages for all vendors")
            cursor.execute("SELECT id FROM vendors")
            vendor_ids = cursor.fetchall()
            for vendor in vendor_ids:
                log_step(logger, 5, f"Sending Kafka message for vendor ID: {vendor['id']}")
                send_data_to_kafka({'vendor_id': vendor['id']})
        log_step(logger, 6, "Raising HTTPException with status code 202")
        raise HTTPException(status_code=202, detail="Data is being fetched, please try again shortly.")
    
    log_step(logger, 7, f"Returning {len(products)} products")
    return {"products": [dict(ix) for ix in products]}

@router.post("/request-vendor-data")
def request_vendor_data(vendor_id: int, conn=Depends(get_db_connection)):
    log_step(logger, 1, f"Received request to fetch data for vendor ID: {vendor_id}")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vendors WHERE id = ?", (vendor_id,))
    vendor = cursor.fetchone()
    if not vendor:
        log_step(logger, 2, f"Invalid vendor ID: {vendor_id}")
        raise HTTPException(status_code=400, detail="Invalid vendor_id")
    log_step(logger, 3, f"Sending Kafka message for vendor ID: {vendor_id}")
    send_data_to_kafka({'vendor_id': vendor_id})
    log_step(logger, 4, f"Data fetch request for vendor {vendor_id} has been sent")
    return {"message": f"Data fetch request for vendor {vendor_id} has been sent."}