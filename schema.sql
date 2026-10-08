CREATE DATABASE IF NOT EXISTS restaurant_pos;
USE restaurant_pos;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_type VARCHAR(20) DEFAULT 'Dine-In',
    payment_mode VARCHAR(20) DEFAULT 'UPI',
    table_no VARCHAR(20) DEFAULT 'Table 1',
    subtotal DECIMAL(10, 2) NOT NULL,
    gst_amount DECIMAL(10, 2) NOT NULL,
    grand_total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Paid',
    kitchen_status VARCHAR(20) DEFAULT 'Preparing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    item_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);