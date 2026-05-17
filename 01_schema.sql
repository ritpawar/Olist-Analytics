-- ============================================
-- 01_schema.sql | Olist E-Commerce Database
-- ============================================
Create Database olist

USE olist;

CREATE TABLE customers (
    customer_id          VARCHAR(40) PRIMARY KEY,
    customer_unique_id   VARCHAR(40) NOT NULL,
    zip_code_prefix      VARCHAR(10),
    city                 VARCHAR(60),
    state                CHAR(2)
);

CREATE TABLE sellers (
    seller_id            VARCHAR(40) PRIMARY KEY,
    zip_code_prefix      VARCHAR(10),
    city                 VARCHAR(60),
    state                CHAR(2)
);

CREATE TABLE products (
    product_id           VARCHAR(40) PRIMARY KEY,
    category_name        VARCHAR(80),
    name_length          INT,
    description_length   INT,
    photos_qty           INT,
    weight_g             DECIMAL(10,2),
    length_cm            DECIMAL(8,2),
    height_cm            DECIMAL(8,2),
    width_cm             DECIMAL(8,2)
);

CREATE TABLE orders (
    order_id                 VARCHAR(40) PRIMARY KEY,
    customer_id              VARCHAR(40),
    order_status             VARCHAR(20) NOT NULL,
    purchase_timestamp       DATETIME,
    approved_at              DATETIME,
    delivered_carrier_at     DATETIME,
    delivered_customer_at    DATETIME,
    estimated_delivery       DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_id             VARCHAR(40),
    order_item_id        INT,
    product_id           VARCHAR(40),
    seller_id            VARCHAR(40),
    shipping_limit_date  DATETIME,
    price                DECIMAL(10,2),
    freight_value        DECIMAL(10,2),
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id)  REFERENCES sellers(seller_id)
);

CREATE TABLE payments (
    order_id             VARCHAR(40),
    payment_sequential   INT,
    payment_type         VARCHAR(20),
    payment_installments INT,
    payment_value        DECIMAL(10,2),
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE reviews (
    review_id        VARCHAR(40),
    order_id         VARCHAR(40),
    score            TINYINT CHECK (score BETWEEN 1 AND 5),
    comment_title    TEXT,
    comment_message  TEXT,
    creation_date    DATETIME,
    answer_timestamp DATETIME,
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE category_translation (
    category_name_portuguese VARCHAR(80),
    category_name_english    VARCHAR(80)
);
