-- ============================================
-- 02_data_quality.sql | Validation Queries
-- ============================================

USE olist;

-- 1. Null audit on orders
SELECT
    COUNT(*)                                                    AS total_rows,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END)       AS null_customer,
    SUM(CASE WHEN purchase_timestamp IS NULL THEN 1 ELSE 0 END) AS null_timestamp,
    SUM(CASE WHEN order_status IS NULL THEN 1 ELSE 0 END)      AS null_status
FROM orders;

-- 2. Duplicate order IDs
SELECT order_id, COUNT(*) AS dupes
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 3. Timestamp violations (approved before purchase)
SELECT order_id, purchase_timestamp, approved_at
FROM orders
WHERE approved_at < purchase_timestamp;

-- 4. Negative or zero prices
SELECT order_id, product_id, price, freight_value
FROM order_items
WHERE price <= 0 OR freight_value < 0;

-- 5. Payment mismatch (items total vs payment total)
WITH item_totals AS (
    SELECT order_id,
           SUM(price + freight_value) AS items_total
    FROM order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT order_id,
           SUM(payment_value) AS pay_total
    FROM payments
    GROUP BY order_id
)
SELECT
    i.order_id,
    ROUND(i.items_total, 2) AS items_total,
    ROUND(p.pay_total, 2)   AS pay_total,
    ROUND(p.pay_total - i.items_total, 2) AS diff
FROM item_totals i
JOIN payment_totals p USING (order_id)
WHERE ABS(p.pay_total - i.items_total) > 0.05
ORDER BY diff DESC
LIMIT 20;

-- 6. Review score distribution
SELECT
    score,
    COUNT(*) AS total,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM reviews
GROUP BY score
ORDER BY score;
