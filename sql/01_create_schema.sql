PRAGMA foreign_keys = ON;

-- ============================================================
-- SASADIAKOPI DATA ANALYSIS
-- Database Schema V1
-- ============================================================


-- ============================================================
-- TABLE: customers
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL
        CHECK (segment IN ('New', 'Regular', 'Loyal')),
    join_date TEXT NOT NULL
);


-- ============================================================
-- TABLE: products
-- ============================================================

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
        CHECK (category IN ('Coffee', 'Non-Coffee', 'Food')),
    cost_price INTEGER NOT NULL
        CHECK (cost_price > 0),
    selling_price INTEGER NOT NULL
        CHECK (selling_price > cost_price)
);


-- ============================================================
-- TABLE: sales
-- ============================================================

CREATE TABLE IF NOT EXISTS sales (
    sale_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT NOT NULL,
    sale_date TEXT NOT NULL,
    quantity INTEGER NOT NULL
        CHECK (quantity > 0),
    unit_price INTEGER NOT NULL
        CHECK (unit_price > 0),
    discount_pct REAL NOT NULL DEFAULT 0
        CHECK (
            discount_pct >= 0
            AND discount_pct <= 100
        ),
    payment_method TEXT NOT NULL
        CHECK (
            payment_method IN (
                'Cash',
                'QRIS',
                'Debit',
                'E-Wallet'
            )
        ),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- ============================================================
-- TABLE: expenses
-- ============================================================

CREATE TABLE IF NOT EXISTS expenses (
    expense_id TEXT PRIMARY KEY,
    expense_date TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (
            category IN (
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
        ),
    description TEXT NOT NULL,
    amount INTEGER NOT NULL
        CHECK (amount > 0)
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_sales_customer_id
ON sales(customer_id);

CREATE INDEX IF NOT EXISTS idx_sales_product_id
ON sales(product_id);

CREATE INDEX IF NOT EXISTS idx_sales_sale_date
ON sales(sale_date);

CREATE INDEX IF NOT EXISTS idx_expenses_expense_date
ON expenses(expense_date);

CREATE INDEX IF NOT EXISTS idx_expenses_category
ON expenses(category);