# backend/app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db_connection
from core.kafka_producer import send_data_to_kafka

router = APIRouter()

@router.get("/products")
def get_products(vendor_id: int = None, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    if vendor_id:
        # Fetch products for a specific vendor
        cursor.execute("""
            SELECT p.*
            FROM products p
            JOIN products_vendors pv ON p.id = pv.product_id
            WHERE pv.vendor_id = ?
        """, (vendor_id,))
    else:
        # Fetch all products
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        # No data, send request to fetch data
        if vendor_id:
            send_data_to_kafka({'vendor_id': vendor_id})
            raise HTTPException(status_code=202, detail="Data is being fetched, please try again shortly.")
        else:
            raise HTTPException(status_code=404, detail="No products found.")
    
    return {"products": [dict(ix) for ix in products]}

@router.post("/request-vendor-data")
def request_vendor_data(vendor_id: int, conn=Depends(get_db_connection)):
    # Check if vendor exists
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vendors WHERE id = ?", (vendor_id,))
    vendor = cursor.fetchone()
    if not vendor:
        raise HTTPException(status_code=400, detail="Invalid vendor_id")
    # Send message to Kafka
    send_data_to_kafka({'vendor_id': vendor_id})
    return {"message": f"Data fetch request for vendor {vendor_id} has been sent."}
