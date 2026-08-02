-- ============================================================
-- SASADIAKOPI DATA ANALYSIS
-- 03 - BUSINESS ANALYSIS
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. SALES OVERVIEW
-- ============================================================

SELECT
    COUNT(*) AS total_transactions,
    SUM(quantity) AS total_items_sold,
    MIN(sale_date) AS first_sale_date,
    MAX(sale_date) AS last_sale_date
FROM sales;


-- ============================================================
-- 2. TOTAL REVENUE
-- Revenue = Quantity × Unit Price × (1 - Discount)
-- ============================================================

SELECT
    ROUND(
        SUM(
            quantity
            * unit_price
            * (1 - discount_pct / 100.0)
        ),
        2
    ) AS total_revenue
FROM sales;


-- ============================================================
-- 3. TOTAL COGS
-- COGS = Quantity × Product Cost Price
-- ============================================================

SELECT
    ROUND(
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS total_cogs
FROM sales AS s
JOIN products AS p
    ON s.product_id = p.product_id;


-- ============================================================
-- 4. GROSS PROFIT
-- Gross Profit = Revenue - COGS
-- ============================================================

SELECT
    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS total_revenue,

    ROUND(
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS total_cogs,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        )
        -
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS gross_profit

FROM sales AS s

JOIN products AS p
    ON s.product_id = p.product_id;


-- ============================================================
-- 5. OPERATING EXPENSES
-- ============================================================

SELECT
    ROUND(
        SUM(amount),
        2
    ) AS total_operating_expenses
FROM expenses;


-- ============================================================
-- 6. NET PROFIT
-- Net Profit = Gross Profit - Operating Expenses
-- ============================================================

WITH sales_summary AS (
    SELECT
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ) AS revenue,

        SUM(
            s.quantity * p.cost_price
        ) AS cogs

    FROM sales AS s

    JOIN products AS p
        ON s.product_id = p.product_id
),

expense_summary AS (
    SELECT
        SUM(amount) AS operating_expenses
    FROM expenses
)

SELECT
    ROUND(revenue, 2) AS revenue,
    ROUND(cogs, 2) AS cogs,
    ROUND(revenue - cogs, 2) AS gross_profit,
    ROUND(operating_expenses, 2) AS operating_expenses,
    ROUND(
        revenue
        - cogs
        - operating_expenses,
        2
    ) AS net_profit

FROM sales_summary
CROSS JOIN expense_summary;


-- ============================================================
-- 7. GROSS PROFIT MARGIN
-- ============================================================

WITH sales_summary AS (
    SELECT
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ) AS revenue,

        SUM(
            s.quantity * p.cost_price
        ) AS cogs

    FROM sales AS s

    JOIN products AS p
        ON s.product_id = p.product_id
)

SELECT
    ROUND(
        (
            (revenue - cogs)
            / NULLIF(revenue, 0)
        ) * 100,
        2
    ) AS gross_profit_margin_pct

FROM sales_summary;


-- ============================================================
-- 8. NET PROFIT MARGIN
-- ============================================================

WITH sales_summary AS (
    SELECT
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ) AS revenue,

        SUM(
            s.quantity * p.cost_price
        ) AS cogs

    FROM sales AS s

    JOIN products AS p
        ON s.product_id = p.product_id
),

expense_summary AS (
    SELECT
        SUM(amount) AS operating_expenses
    FROM expenses
)

SELECT
    ROUND(
        (
            (
                revenue
                - cogs
                - operating_expenses
            )
            / NULLIF(revenue, 0)
        ) * 100,
        2
    ) AS net_profit_margin_pct

FROM sales_summary
CROSS JOIN expense_summary;


-- ============================================================
-- 9. REVENUE BY PRODUCT
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,

    SUM(s.quantity) AS units_sold,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS revenue

FROM sales AS s

JOIN products AS p
    ON s.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category

ORDER BY revenue DESC;


-- ============================================================
-- 10. GROSS PROFIT BY PRODUCT
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,

    SUM(s.quantity) AS units_sold,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS revenue,

    ROUND(
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS cogs,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        )
        -
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS gross_profit

FROM sales AS s

JOIN products AS p
    ON s.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category

ORDER BY gross_profit DESC;


-- ============================================================
-- 11. REVENUE BY CATEGORY
-- ============================================================

SELECT
    p.category,

    SUM(s.quantity) AS units_sold,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS revenue

FROM sales AS s

JOIN products AS p
    ON s.product_id = p.product_id

GROUP BY
    p.category

ORDER BY revenue DESC;


-- ============================================================
-- 12. REVENUE BY PAYMENT METHOD
-- ============================================================

SELECT
    payment_method,

    COUNT(*) AS transactions,

    SUM(quantity) AS items_sold,

    ROUND(
        SUM(
            quantity
            * unit_price
            * (1 - discount_pct / 100.0)
        ),
        2
    ) AS revenue

FROM sales

GROUP BY
    payment_method

ORDER BY revenue DESC;


-- ============================================================
-- 13. CUSTOMER SEGMENT PERFORMANCE
-- ============================================================

SELECT
    c.segment,

    COUNT(DISTINCT c.customer_id) AS customers,

    COUNT(s.sale_id) AS transactions,

    SUM(s.quantity) AS items_sold,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS revenue

FROM customers AS c

LEFT JOIN sales AS s
    ON c.customer_id = s.customer_id

GROUP BY
    c.segment

ORDER BY revenue DESC;


-- ============================================================
-- 14. MONTHLY REVENUE
-- ============================================================

SELECT
    strftime('%Y-%m', sale_date) AS month,

    COUNT(*) AS transactions,

    SUM(quantity) AS items_sold,

    ROUND(
        SUM(
            quantity
            * unit_price
            * (1 - discount_pct / 100.0)
        ),
        2
    ) AS revenue

FROM sales

GROUP BY
    strftime('%Y-%m', sale_date)

ORDER BY month;


-- ============================================================
-- 15. MONTHLY GROSS PROFIT
-- ============================================================

SELECT
    strftime('%Y-%m', s.sale_date) AS month,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ),
        2
    ) AS revenue,

    ROUND(
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS cogs,

    ROUND(
        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        )
        -
        SUM(
            s.quantity * p.cost_price
        ),
        2
    ) AS gross_profit

FROM sales AS s

JOIN products AS p
    ON s.product_id = p.product_id

GROUP BY
    strftime('%Y-%m', s.sale_date)

ORDER BY month;


-- ============================================================
-- 16. EXPENSE BY CATEGORY
-- ============================================================

SELECT
    category,

    COUNT(*) AS records,

    ROUND(
        SUM(amount),
        2
    ) AS total_expense

FROM expenses

GROUP BY
    category

ORDER BY total_expense DESC;


-- ============================================================
-- 17. MONTHLY EXPENSE
-- ============================================================

SELECT
    strftime('%Y-%m', expense_date) AS month,

    ROUND(
        SUM(amount),
        2
    ) AS total_expense

FROM expenses

GROUP BY
    strftime('%Y-%m', expense_date)

ORDER BY month;


-- ============================================================
-- 18. MONTHLY PROFITABILITY
-- Revenue - COGS - Operating Expenses
-- ============================================================

WITH monthly_sales AS (
    SELECT
        strftime('%Y-%m', s.sale_date) AS month,

        SUM(
            s.quantity
            * s.unit_price
            * (1 - s.discount_pct / 100.0)
        ) AS revenue,

        SUM(
            s.quantity * p.cost_price
        ) AS cogs

    FROM sales AS s

    JOIN products AS p
        ON s.product_id = p.product_id

    GROUP BY
        strftime('%Y-%m', s.sale_date)
),

monthly_expenses AS (
    SELECT
        strftime('%Y-%m', expense_date) AS month,

        SUM(amount) AS operating_expenses

    FROM expenses

    GROUP BY
        strftime('%Y-%m', expense_date)
)

SELECT
    ms.month,

    ROUND(ms.revenue, 2) AS revenue,

    ROUND(ms.cogs, 2) AS cogs,

    ROUND(
        ms.revenue - ms.cogs,
        2
    ) AS gross_profit,

    ROUND(
        COALESCE(me.operating_expenses, 0),
        2
    ) AS operating_expenses,

    ROUND(
        ms.revenue
        - ms.cogs
        - COALESCE(me.operating_expenses, 0),
        2
    ) AS net_profit

FROM monthly_sales AS ms

LEFT JOIN monthly_expenses AS me
    ON ms.month = me.month

ORDER BY ms.month;