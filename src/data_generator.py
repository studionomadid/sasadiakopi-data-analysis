"""Synthetic data generator for the Sasadiakopi data analysis project."""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "sasadiakopi.db"

RANDOM_SEED = 42

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

CUSTOMER_COUNT = 300
SALES_COUNT = 5000


# ============================================================
# RANDOM GENERATOR
# ============================================================

random_generator = random.Random(RANDOM_SEED)


# ============================================================
# MASTER PRODUCT DATA
# ============================================================

PRODUCTS = [
    {
        "product_id": "P001",
        "product_name": "Es Kopi Susu Sasadiakopi",
        "category": "Coffee",
        "cost_price": 8000,
        "selling_price": 18000,
    },
    {
        "product_id": "P002",
        "product_name": "Americano",
        "category": "Coffee",
        "cost_price": 5000,
        "selling_price": 15000,
    },
    {
        "product_id": "P003",
        "product_name": "Cafe Latte",
        "category": "Coffee",
        "cost_price": 7000,
        "selling_price": 20000,
    },
    {
        "product_id": "P004",
        "product_name": "Cappuccino",
        "category": "Coffee",
        "cost_price": 7000,
        "selling_price": 20000,
    },
    {
        "product_id": "P005",
        "product_name": "Mocha",
        "category": "Coffee",
        "cost_price": 8000,
        "selling_price": 22000,
    },
    {
        "product_id": "P006",
        "product_name": "Matcha Latte",
        "category": "Non-Coffee",
        "cost_price": 8000,
        "selling_price": 20000,
    },
    {
        "product_id": "P007",
        "product_name": "Chocolate",
        "category": "Non-Coffee",
        "cost_price": 7000,
        "selling_price": 18000,
    },
    {
        "product_id": "P008",
        "product_name": "Lychee Tea",
        "category": "Non-Coffee",
        "cost_price": 5000,
        "selling_price": 15000,
    },
    {
        "product_id": "P009",
        "product_name": "French Fries",
        "category": "Food",
        "cost_price": 7000,
        "selling_price": 16000,
    },
    {
        "product_id": "P010",
        "product_name": "Chicken Sandwich",
        "category": "Food",
        "cost_price": 10000,
        "selling_price": 22000,
    },
    {
        "product_id": "P011",
        "product_name": "Churros",
        "category": "Food",
        "cost_price": 8000,
        "selling_price": 18000,
    },
    {
        "product_id": "P012",
        "product_name": "Toast",
        "category": "Food",
        "cost_price": 6000,
        "selling_price": 15000,
    },
]


# ============================================================
# CUSTOMER MASTER DATA
# ============================================================

CUSTOMER_FIRST_NAMES = [
    "Andi",
    "Bima",
    "Citra",
    "Dinda",
    "Eka",
    "Fajar",
    "Gilang",
    "Hana",
    "Intan",
    "Joko",
    "Karin",
    "Lukman",
    "Maya",
    "Nadia",
    "Oki",
    "Putri",
    "Raka",
    "Salsa",
    "Tio",
    "Vina",
]

CUSTOMER_LAST_NAMES = [
    "Pratama",
    "Saputra",
    "Wijaya",
    "Permata",
    "Nugraha",
    "Ramadhan",
    "Kusuma",
    "Santoso",
    "Hidayat",
    "Lestari",
]


# ============================================================
# PAYMENT METHODS
# ============================================================

PAYMENT_METHODS = [
    "Cash",
    "QRIS",
    "Debit",
    "E-Wallet",
]

PAYMENT_METHOD_WEIGHTS = [
    0.35,
    0.40,
    0.10,
    0.15,
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# ============================================================
# CUSTOMER GENERATION
# ============================================================

def generate_customer_name() -> str:
    """Generate a synthetic customer name."""
    first_name = random_generator.choice(CUSTOMER_FIRST_NAMES)
    last_name = random_generator.choice(CUSTOMER_LAST_NAMES)

    return f"{first_name} {last_name}"


def generate_customer_segment() -> str:
    """Generate a customer segment using realistic probabilities."""
    return random_generator.choices(
        population=["New", "Regular", "Loyal"],
        weights=[0.35, 0.45, 0.20],
        k=1,
    )[0]


def generate_customer_join_date() -> str:
    """Generate a customer join date within the analysis period."""
    days_range = (END_DATE - START_DATE).days

    random_days = random_generator.randint(0, days_range)

    join_date = START_DATE + timedelta(days=random_days)

    return join_date.isoformat()


def generate_customers(
    count: int = CUSTOMER_COUNT,
) -> list[dict[str, str]]:
    """Generate synthetic customer records."""
    customers: list[dict[str, str]] = []

    for index in range(1, count + 1):
        customers.append(
            {
                "customer_id": f"C{index:04d}",
                "customer_name": generate_customer_name(),
                "segment": generate_customer_segment(),
                "join_date": generate_customer_join_date(),
            }
        )

    return customers


# ============================================================
# SALES GENERATION
# ============================================================

def generate_sale_date() -> str:
    """Generate a random sale date within the analysis period."""
    days_range = (END_DATE - START_DATE).days

    random_days = random_generator.randint(0, days_range)

    sale_date = START_DATE + timedelta(days=random_days)

    return sale_date.isoformat()


def generate_quantity() -> int:
    """Generate a realistic purchase quantity."""
    return random_generator.choices(
        population=[1, 2, 3, 4],
        weights=[0.60, 0.25, 0.10, 0.05],
        k=1,
    )[0]


def generate_discount_pct() -> float:
    """Generate a realistic discount percentage."""
    has_discount = random_generator.random() < 0.20

    if not has_discount:
        return 0.0

    return random_generator.choice(
        [
            5.0,
            10.0,
            15.0,
            20.0,
        ]
    )


def generate_payment_method() -> str:
    """Generate a payment method using realistic probabilities."""
    return random_generator.choices(
        population=PAYMENT_METHODS,
        weights=PAYMENT_METHOD_WEIGHTS,
        k=1,
    )[0]


def generate_product() -> dict[str, str | int]:
    """Select a product using weighted product popularity."""
    product_weights = [
        0.20,
        0.10,
        0.08,
        0.07,
        0.05,
        0.08,
        0.07,
        0.05,
        0.07,
        0.06,
        0.10,
        0.07,
    ]

    return random_generator.choices(
        population=PRODUCTS,
        weights=product_weights,
        k=1,
    )[0]


def generate_customer(
    customers: list[dict[str, str]],
) -> dict[str, str]:
    """Select a customer for a transaction."""
    return random_generator.choice(customers)


def generate_sale(
    sale_number: int,
    customers: list[dict[str, str]],
) -> dict[str, str | int | float]:
    """Generate a single synthetic sales transaction."""
    product = generate_product()
    customer = generate_customer(customers)

    return {
        "sale_id": f"S{sale_number:06d}",
        "customer_id": customer["customer_id"],
        "product_id": product["product_id"],
        "sale_date": generate_sale_date(),
        "quantity": generate_quantity(),
        "unit_price": product["selling_price"],
        "discount_pct": generate_discount_pct(),
        "payment_method": generate_payment_method(),
    }


def generate_sales(
    customers: list[dict[str, str]],
    count: int = SALES_COUNT,
) -> list[dict[str, str | int | float]]:
    """Generate synthetic sales transactions."""
    return [
        generate_sale(
            sale_number=index,
            customers=customers,
        )
        for index in range(1, count + 1)
    ]


# ============================================================
# DATABASE INSERTION
# ============================================================

def insert_customers(
    connection: sqlite3.Connection,
    customers: list[dict[str, str]],
) -> None:
    """Insert generated customers into the database."""
    connection.executemany(
        """
        INSERT INTO customers (
            customer_id,
            customer_name,
            segment,
            join_date
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                customer["customer_id"],
                customer["customer_name"],
                customer["segment"],
                customer["join_date"],
            )
            for customer in customers
        ],
    )

    connection.commit()


def insert_products(
    connection: sqlite3.Connection,
    products: list[dict[str, str | int]],
) -> None:
    """Insert product master data into the database."""
    connection.executemany(
        """
        INSERT INTO products (
            product_id,
            product_name,
            category,
            cost_price,
            selling_price
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                product["product_id"],
                product["product_name"],
                product["category"],
                product["cost_price"],
                product["selling_price"],
            )
            for product in products
        ],
    )

    connection.commit()


def insert_sales(
    connection: sqlite3.Connection,
    sales: list[dict[str, str | int | float]],
) -> None:
    """Insert generated sales transactions into the database."""
    connection.executemany(
        """
        INSERT INTO sales (
            sale_id,
            customer_id,
            product_id,
            sale_date,
            quantity,
            unit_price,
            discount_pct,
            payment_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                sale["sale_id"],
                sale["customer_id"],
                sale["product_id"],
                sale["sale_date"],
                sale["quantity"],
                sale["unit_price"],
                sale["discount_pct"],
                sale["payment_method"],
            )
            for sale in sales
        ],
    )

    connection.commit()


# ============================================================
# EXPENSE GENERATION
# ============================================================

EXPENSE_CATEGORIES = [
    "Rent",
    "Electricity",
    "Water",
    "Internet",
    "Gas",
    "Salary",
    "Marketing",
    "Maintenance",
    "Other",
]


EXPENSE_DESCRIPTIONS = {
    "Rent": "Monthly shop rent",
    "Electricity": "Monthly electricity bill",
    "Water": "Monthly water bill",
    "Internet": "Monthly internet bill",
    "Gas": "Cooking gas refill",
    "Salary": "Staff salary",
    "Marketing": "Marketing and promotion",
    "Maintenance": "Equipment maintenance",
    "Other": "Other operational expense",
}


def generate_expense_amount(category: str) -> int:
    """Generate a realistic expense amount based on category."""
    ranges = {
        "Rent": (2_000_000, 4_000_000),
        "Electricity": (150_000, 350_000),
        "Water": (80_000, 200_000),
        "Internet": (200_000, 400_000),
        "Gas": (20_000, 100_000),
        "Salary": (1_500_000, 3_000_000),
        "Marketing": (100_000, 500_000),
        "Maintenance": (100_000, 750_000),
        "Other": (50_000, 300_000),
    }

    minimum, maximum = ranges[category]

    return random_generator.randint(minimum, maximum)


def generate_expenses(
    year: int = 2025,
) -> list[dict[str, str | int]]:
    """Generate synthetic monthly operating expenses."""
    expenses: list[dict[str, str | int]] = []

    expense_number = 1

    for month in range(1, 13):
        for category in EXPENSE_CATEGORIES:
            expense_date = date(year, month, 1)

            expenses.append(
                {
                    "expense_id": f"E{expense_number:04d}",
                    "expense_date": expense_date.isoformat(),
                    "category": category,
                    "description": EXPENSE_DESCRIPTIONS[category],
                    "amount": generate_expense_amount(category),
                }
            )

            expense_number += 1

    return expenses


def insert_expenses(
    connection: sqlite3.Connection,
    expenses: list[dict[str, str | int]],
) -> None:
    """Insert generated expenses into the database."""
    connection.executemany(
        """
        INSERT INTO expenses (
            expense_id,
            expense_date,
            category,
            description,
            amount
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                expense["expense_id"],
                expense["expense_date"],
                expense["category"],
                expense["description"],
                expense["amount"],
            )
            for expense in expenses
        ],
    )

    connection.commit()


# ============================================================
# MAIN PIPELINE
# ============================================================

def main() -> None:
    """Generate and load the complete synthetic dataset."""
    connection = get_connection()

    try:
        customers = generate_customers()
        expenses = generate_expenses()

        connection.execute("DELETE FROM sales")
        connection.execute("DELETE FROM expenses")
        connection.execute("DELETE FROM customers")
        connection.execute("DELETE FROM products")

        insert_customers(connection, customers)
        insert_products(connection, PRODUCTS)

        sales = generate_sales(customers)
        insert_sales(connection, sales)
        insert_expenses(connection, expenses)

        print("Synthetic dataset generated successfully.")
        print(f"Customers: {len(customers)}")
        print(f"Products: {len(PRODUCTS)}")
        print(f"Sales: {len(sales)}")
        print(f"Expenses: {len(expenses)}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
