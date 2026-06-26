CREATE DATABASE IF NOT EXISTS nexus_intelligence;
USE nexus_intelligence;

-- ============================================================
-- REFERENCE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id          INT PRIMARY KEY,
    segment_name        VARCHAR(255),
    description         TEXT,
    discount_eligibility BOOLEAN
);

CREATE TABLE IF NOT EXISTS regions (
    region_id           INT PRIMARY KEY,
    region_name         VARCHAR(255),
    country             VARCHAR(255),
    manager_id          INT,
    created_at          DATETIME
);

CREATE TABLE IF NOT EXISTS product_categories (
    category_id         INT PRIMARY KEY,
    category_name       VARCHAR(255),
    parent_category_id  INT,
    description         TEXT
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id        INT PRIMARY KEY,
    warehouse_name      VARCHAR(255),
    location            VARCHAR(255),
    capacity            INT,
    manager_name        VARCHAR(255)
);

-- ============================================================
-- CORE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id         VARCHAR(50) PRIMARY KEY,
    first_name          VARCHAR(255),
    last_name           VARCHAR(255),
    email               VARCHAR(255),
    phone               VARCHAR(50),
    segment_id          INT,
    region_id           INT,
    created_at          DATETIME,
    FOREIGN KEY (segment_id) REFERENCES customer_segments(segment_id),
    FOREIGN KEY (region_id)  REFERENCES regions(region_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id          VARCHAR(50) PRIMARY KEY,
    product_name        VARCHAR(255),
    sku_code            VARCHAR(100),
    category_id         INT,
    price               DECIMAL(10,2),
    cost                DECIMAL(10,2),
    created_at          DATETIME,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id        INT PRIMARY KEY AUTO_INCREMENT,
    product_id          VARCHAR(50),
    warehouse_id        INT,
    quantity_on_hand    INT,
    reorder_level       INT,
    reorder_qty         INT,
    last_updated        DATETIME,
    status              VARCHAR(50),
    FOREIGN KEY (product_id)    REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id            INT PRIMARY KEY AUTO_INCREMENT,
    customer_id         VARCHAR(50),
    region_id           INT,
    order_date          DATETIME,
    total_amount        DECIMAL(10,2),
    discount_amount     DECIMAL(10,2),
    net_amount          DECIMAL(10,2),
    status              VARCHAR(50),
    payment_method      VARCHAR(50),
    created_at          DATETIME,
    FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
    FOREIGN KEY (region_id)     REFERENCES regions(region_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id             INT PRIMARY KEY AUTO_INCREMENT,
    order_id            INT,
    product_id          VARCHAR(50),
    quantity            INT,
    unit_price          DECIMAL(10,2),
    discount_pct        DECIMAL(5,2),
    line_total          DECIMAL(10,2),
    FOREIGN KEY (order_id)      REFERENCES orders(order_id),
    FOREIGN KEY (product_id)    REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id          INT PRIMARY KEY AUTO_INCREMENT,
    order_id            INT,
    payment_method      VARCHAR(50),
    amount              DECIMAL(10,2),
    status              VARCHAR(50),
    transaction_id      VARCHAR(100),
    paid_at             DATETIME,
    FOREIGN KEY (order_id)      REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS returns (
    return_id           INT PRIMARY KEY AUTO_INCREMENT,
    order_id            INT,
    product_id          VARCHAR(50),
    customer_id         VARCHAR(50),
    return_reason       VARCHAR(255),
    return_amount       DECIMAL(10,2),
    status              VARCHAR(50),
    created_at          DATETIME,
    FOREIGN KEY (order_id)      REFERENCES orders(order_id),
    FOREIGN KEY (product_id)    REFERENCES products(product_id),
    FOREIGN KEY (customer_id)   REFERENCES customers(customer_id)
);

-- ============================================================
-- ANALYTICS TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS monthly_revenue_summary (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    month               DATE,
    region_id           INT,
    segment_id          INT,
    gross_revenue       DECIMAL(15,2),
    net_revenue         DECIMAL(15,2),
    total_orders        INT,
    total_customers     INT,
    return_value        DECIMAL(15,2),
    discount_value      DECIMAL(15,2),
    target_revenue      DECIMAL(15,2)
);

CREATE TABLE IF NOT EXISTS kpi_snapshots (
    snapshot_id         INT PRIMARY KEY AUTO_INCREMENT,
    snapshot_date       DATE,
    total_revenue       DECIMAL(15,2),
    total_orders        INT,
    total_customers     INT,
    avg_order_value     DECIMAL(10,2),
    gross_margin_pct    DECIMAL(5,2),
    return_rate_pct     DECIMAL(5,2),
    nps_score           INT,
    retention_rate      DECIMAL(5,2),
    inventory_fill_pct  DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS sales_activity_log (
    log_id              INT PRIMARY KEY AUTO_INCREMENT,
    log_date            DATE,
    day_of_week         VARCHAR(20),
    hour_slot           VARCHAR(10),
    activity_pct        DECIMAL(10,4),
    order_count         INT,
    revenue             DECIMAL(15,2)
);

CREATE TABLE IF NOT EXISTS customer_health_metrics (
    id                      INT PRIMARY KEY AUTO_INCREMENT,
    snapshot_date           DATE,
    nps_score               INT,
    retention_rate          DECIMAL(5,2),
    repeat_purchase_rate    DECIMAL(5,2),
    satisfaction_score      DECIMAL(5,2),
    support_csat            DECIMAL(5,2),
    lifetime_value_index    DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id            INT PRIMARY KEY AUTO_INCREMENT,
    alert_type          VARCHAR(50),
    message             TEXT,
    is_read             BOOLEAN DEFAULT FALSE,
    created_at          DATETIME
);
