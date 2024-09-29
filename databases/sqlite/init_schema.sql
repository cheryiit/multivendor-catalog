-- Create vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    site TEXT NOT NULL,
    api_url TEXT NOT NULL
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL
);

-- Create products_vendors table for many-to-many relationship
CREATE TABLE IF NOT EXISTS products_vendors (
    product_id INTEGER,
    vendor_id INTEGER,
    PRIMARY KEY (product_id, vendor_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);
