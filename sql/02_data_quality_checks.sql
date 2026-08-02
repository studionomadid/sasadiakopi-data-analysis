-- ============================================================
-- SASADIAKOPI DATA ANALYSIS
-- 02 - DATA QUALITY CHECKS
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. TABLE ROW COUNTS
-- ============================================================

SELECT
    'customers' AS table_name,
    COUNT(*) AS row_count
FROM customers

UNION ALL

SELECT
    'products',
    COUNT(*)
FROM products

UNION ALL

SELECT
    'sales',
    COUNT(*)
FROM sales

UNION ALL

SELECT
    'expenses',
    COUNT(*)
FROM expenses;


-- ============================================================
-- 2. DATABASE INTEGRITY CHECK
-- ============================================================

PRAGMA integrity_check;


-- ============================================================
-- 3. CUSTOMER DATA QUALITY
-- ============================================================

SELECT
    COUNT(*) AS invalid_customers
FROM customers
WHERE
    customer_id IS NULL
    OR customer_id = ''
    OR customer_name IS NULL
    OR customer_name = ''
    OR segment NOT IN ('New', 'Regular', 'Loyal')
    OR join_date IS NULL
    OR join_date = '';


-- ============================================================
-- 4. PRODUCT DATA QUALITY
-- ============================================================

SELECT
    COUNT(*) AS invalid_products
FROM products
WHERE
    product_id IS NULL
    OR product_id = ''
    OR product_name IS NULL
    OR product_name = ''
    OR category NOT IN ('Coffee', 'Non-Coffee', 'Food')
    OR cost_price <= 0
    OR selling_price <= 0
    OR selling_price <= cost_price;


-- ============================================================
-- 5. SALES DATA QUALITY
-- ============================================================

SELECT
    COUNT(*) AS invalid_sales
FROM sales
WHERE
    sale_id IS NULL
    OR sale_id = ''
    OR customer_id IS NULL
    OR product_id IS NULL
    OR sale_date IS NULL
    OR sale_date = ''
    OR quantity <= 0
    OR unit_price <= 0
    OR discount_pct < 0
    OR discount_pct > 100
    OR payment_method NOT IN (
        'Cash',
        'QRIS',
        'Debit',
        'E-Wallet'
    );


-- ============================================================
-- 6. EXPENSE DATA QUALITY
-- ============================================================

SELECT
    COUNT(*) AS invalid_expenses
FROM expenses
WHERE
    expense_id IS NULL
    OR expense_id = ''
    OR expense_date IS NULL
    OR expense_date = ''
    OR category NOT IN (
        'Rent',
        'Electricity',
        'Water',
        'Internet',
        'Gas',
        'Salary',
        'Marketing',
        'Maintenance',
        'Other'
    )
    OR description IS NULL
    OR description = ''
    OR amount <= 0;


-- ============================================================
-- 7. DUPLICATE CUSTOMER IDs
-- ============================================================

SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 8. DUPLICATE PRODUCT IDs
-- ============================================================

SELECT
    product_id,
    COUNT(*) AS duplicate_count
FROM products
GROUP BY product_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 9. DUPLICATE SALE IDs
-- ============================================================

SELECT
    sale_id,
    COUNT(*) AS duplicate_count
FROM sales
GROUP BY sale_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 10. DUPLICATE EXPENSE IDs
-- ============================================================

SELECT
    expense_id,
    COUNT(*) AS duplicate_count
FROM expenses
GROUP BY expense_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 11. ORPHAN SALES
-- ============================================================

SELECT
    COUNT(*) AS orphan_sales
FROM sales AS s
LEFT JOIN customers AS c
    ON s.customer_id = c.customer_id
LEFT JOIN products AS p
    ON s.product_id = p.product_id
WHERE
    c.customer_id IS NULL
    OR p.product_id IS NULL;


-- ============================================================
-- 12. DATE RANGE CHECK
-- ============================================================

SELECT
    'sales' AS table_name,
    MIN(sale_date) AS minimum_date,
    MAX(sale_date) AS maximum_date
FROM sales

UNION ALL

SELECT
    'customers',
    MIN(join_date),
    MAX(join_date)
FROM customers

UNION ALL

SELECT
    'expenses',
    MIN(expense_date),
    MAX(expense_date)
FROM expenses;


-- ============================================================
-- 13. SALES PAYMENT METHOD DISTRIBUTION
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS transaction_count
FROM sales
GROUP BY payment_method
ORDER BY transaction_count DESC;


-- ============================================================
-- 14. CUSTOMER SEGMENT DISTRIBUTION
-- ============================================================

SELECT
    segment,
    COUNT(*) AS customer_count
FROM customers
GROUP BY segment
ORDER BY customer_count DESC;


-- ============================================================
-- 15. PRODUCT CATEGORY DISTRIBUTION
-- ============================================================

SELECT
    category,
    COUNT(*) AS product_count
FROM products
GROUP BY category
ORDER BY product_count DESC;