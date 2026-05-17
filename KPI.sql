-- ============================================
-- 03_kpis.sql | Business KPI
-- ============================================

USE olist;

-- KPI 1: Monthly revenue trend
SELECT
    DATE_FORMAT(o.purchase_timestamp, '%Y-%m') AS month,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    ROUND(SUM(p.payment_value), 2)              AS gross_revenue,
    ROUND(AVG(p.payment_value), 2)              AS avg_order_value
FROM orders o
JOIN payments p USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.purchase_timestamp, '%Y-%m')
ORDER BY month;

-- KPI 2: Delivery time by state
SELECT
    c.state,
    COUNT(*) AS total_orders,
    ROUND(AVG(DATEDIFF(o.delivered_customer_at,
        o.purchase_timestamp)), 1)              AS actual_days,
    ROUND(AVG(DATEDIFF(o.estimated_delivery,
        o.purchase_timestamp)), 1)              AS promised_days,
    ROUND(AVG(DATEDIFF(o.estimated_delivery,
        o.delivered_customer_at)), 1)           AS days_early_late
FROM orders o
JOIN customers c USING (customer_id)
WHERE o.order_status = 'delivered'
AND o.delivered_customer_at IS NOT NULL
GROUP BY c.state
ORDER BY actual_days DESC;

-- KPI 3: Seller performance scorecard
SELECT
    i.seller_id,
    COUNT(DISTINCT i.order_id)                       AS total_orders,
    ROUND(SUM(i.price), 2)                           AS total_revenue,
    ROUND(AVG(r.score), 2)                           AS avg_review_score,
    SUM(CASE WHEN r.score <= 2 THEN 1 ELSE 0 END)   AS poor_reviews
FROM order_items i
JOIN orders o USING (order_id)
LEFT JOIN reviews r USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY i.seller_id
HAVING COUNT(DISTINCT i.order_id) >= 10
ORDER BY avg_review_score ASC;

-- KPI 4: Category revenue and satisfaction
SELECT
    COALESCE(t.category_name_english,
             p.category_name)              AS category_name,
    COUNT(DISTINCT i.order_id)             AS total_orders,
    ROUND(SUM(i.price), 2)                AS revenue,
    ROUND(AVG(r.score), 2)                AS avg_score
FROM order_items i
JOIN products p USING (product_id)
JOIN orders o USING (order_id)
LEFT JOIN reviews r USING (order_id)
LEFT JOIN category_translation t
    ON p.category_name = t.category_name_portuguese
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(t.category_name_english, p.category_name)
ORDER BY revenue DESC
LIMIT 20;

-- KPI 5: Weekly late delivery rate
SELECT
    DATE_FORMAT(purchase_timestamp, '%Y-%u') AS week,
    COUNT(*)                                  AS total_orders,
    SUM(CASE WHEN delivered_customer_at > estimated_delivery
        THEN 1 ELSE 0 END)                    AS late_orders,
    ROUND(100.0 * SUM(CASE WHEN delivered_customer_at > estimated_delivery
        THEN 1 ELSE 0 END) / COUNT(*), 1)     AS late_pct
FROM orders
WHERE order_status = 'delivered'
AND delivered_customer_at IS NOT NULL
GROUP BY DATE_FORMAT(purchase_timestamp, '%Y-%u')
HAVING COUNT(*) >= 10
ORDER BY week;