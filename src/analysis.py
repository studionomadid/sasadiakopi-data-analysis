"""Business analysis utilities for the Sasadiakopi data analysis project."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "sasadiakopi.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# ============================================================
# DATA LOADING
# ============================================================

def load_customers(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Load customer data into a pandas DataFrame."""
    query = """
        SELECT
            customer_id,
            customer_name,
            segment,
            join_date
        FROM customers
        ORDER BY customer_id
    """

    dataframe = pd.read_sql_query(query, connection)

    dataframe["join_date"] = pd.to_datetime(
        dataframe["join_date"],
    )

    return dataframe


def load_products(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Load product data into a pandas DataFrame."""
    query = """
        SELECT
            product_id,
            product_name,
            category,
            cost_price,
            selling_price
        FROM products
        ORDER BY product_id
    """

    return pd.read_sql_query(query, connection)


def load_sales(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Load sales data into a pandas DataFrame."""
    query = """
        SELECT
            sale_id,
            customer_id,
            product_id,
            sale_date,
            quantity,
            unit_price,
            discount_pct,
            payment_method
        FROM sales
        ORDER BY sale_date, sale_id
    """

    dataframe = pd.read_sql_query(query, connection)

    dataframe["sale_date"] = pd.to_datetime(
        dataframe["sale_date"],
    )

    return dataframe


def load_expenses(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Load expense data into a pandas DataFrame."""
    query = """
        SELECT
            expense_id,
            expense_date,
            category,
            description,
            amount
        FROM expenses
        ORDER BY expense_date, expense_id
    """

    dataframe = pd.read_sql_query(query, connection)

    dataframe["expense_date"] = pd.to_datetime(
        dataframe["expense_date"],
    )

    return dataframe


# ============================================================
# DATASET LOADING
# ============================================================

def load_all_data(
    connection: sqlite3.Connection,
) -> dict[str, pd.DataFrame]:
    """Load all project datasets into pandas DataFrames."""
    return {
        "customers": load_customers(connection),
        "products": load_products(connection),
        "sales": load_sales(connection),
        "expenses": load_expenses(connection),
    }


# ============================================================
# DATASET SUMMARY
# ============================================================

def summarize_datasets(
    datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Return row and column counts for every dataset."""
    summary: list[dict[str, int | str]] = []

    for name, dataframe in datasets.items():
        summary.append(
            {
                "dataset": name,
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
            }
        )

    return pd.DataFrame(summary)


# ============================================================
# SALES METRICS
# ============================================================

def calculate_sales_metrics(
    sales: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue, COGS, and gross profit for each sale."""
    dataframe = sales.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
                "cost_price",
            ]
        ],
        on="product_id",
        how="left",
    )

    dataframe["gross_sales"] = (
        dataframe["quantity"]
        * dataframe["unit_price"]
    )

    dataframe["discount_amount"] = (
        dataframe["gross_sales"]
        * dataframe["discount_pct"]
        / 100
    )

    dataframe["net_sales"] = (
        dataframe["gross_sales"]
        - dataframe["discount_amount"]
    )

    dataframe["cogs"] = (
        dataframe["quantity"]
        * dataframe["cost_price"]
    )

    dataframe["gross_profit"] = (
        dataframe["net_sales"]
        - dataframe["cogs"]
    )

    return dataframe


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

def calculate_product_performance(
    sales_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate sales performance by product."""
    dataframe = (
        sales_metrics
        .groupby(
            [
                "product_id",
                "product_name",
                "category",
            ],
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("net_sales", "sum"),
            cogs=("cogs", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values(
            "revenue",
            ascending=False,
        )
    )

    dataframe["gross_margin_pct"] = (
        dataframe["gross_profit"]
        / dataframe["revenue"]
        * 100
    )

    return dataframe


# ============================================================
# CATEGORY PERFORMANCE
# ============================================================

def calculate_category_performance(
    sales_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate sales performance by product category."""
    dataframe = (
        sales_metrics
        .groupby(
            "category",
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("net_sales", "sum"),
            cogs=("cogs", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values(
            "revenue",
            ascending=False,
        )
    )

    dataframe["gross_margin_pct"] = (
        dataframe["gross_profit"]
        / dataframe["revenue"]
        * 100
    )

    return dataframe


# ============================================================
# PAYMENT METHOD PERFORMANCE
# ============================================================

def calculate_payment_performance(
    sales_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue performance by payment method."""
    return (
        sales_metrics
        .groupby(
            "payment_method",
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("net_sales", "sum"),
        )
        .sort_values(
            "revenue",
            ascending=False,
        )
    )


# ============================================================
# CUSTOMER SEGMENT PERFORMANCE
# ============================================================

def calculate_customer_segment_performance(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate sales performance by customer segment."""
    dataframe = sales.merge(
        customers[
            [
                "customer_id",
                "segment",
            ]
        ],
        on="customer_id",
        how="left",
    )

    dataframe["gross_sales"] = (
        dataframe["quantity"]
        * dataframe["unit_price"]
    )

    dataframe["discount_amount"] = (
        dataframe["gross_sales"]
        * dataframe["discount_pct"]
        / 100
    )

    dataframe["net_sales"] = (
        dataframe["gross_sales"]
        - dataframe["discount_amount"]
    )

    return (
        dataframe
        .groupby(
            "segment",
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("net_sales", "sum"),
            unique_customers=("customer_id", "nunique"),
        )
        .sort_values(
            "revenue",
            ascending=False,
        )
    )


# ============================================================
# EXPENSE SUMMARY
# ============================================================

def calculate_expense_summary(
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate total operating expenses by category."""
    return (
        expenses
        .groupby(
            "category",
            as_index=False,
        )
        .agg(
            expense_count=("expense_id", "count"),
            total_expense=("amount", "sum"),
        )
        .sort_values(
            "total_expense",
            ascending=False,
        )
    )


# ============================================================
# MONTHLY SALES PERFORMANCE
# ============================================================

def calculate_monthly_sales(
    sales_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly sales and gross profit."""
    dataframe = sales_metrics.copy()

    dataframe["month"] = (
        dataframe["sale_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        dataframe
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("net_sales", "sum"),
            cogs=("cogs", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("month")
    )


# ============================================================
# MONTHLY EXPENSE PERFORMANCE
# ============================================================

def calculate_monthly_expenses(
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly operating expenses."""
    dataframe = expenses.copy()

    dataframe["month"] = (
        dataframe["expense_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        dataframe
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            total_expense=("amount", "sum"),
        )
        .sort_values("month")
    )


# ============================================================
# MONTHLY PROFITABILITY
# ============================================================

def calculate_monthly_profitability(
    monthly_sales: pd.DataFrame,
    monthly_expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly gross and net profit."""
    dataframe = monthly_sales.merge(
        monthly_expenses,
        on="month",
        how="left",
    )

    dataframe["total_expense"] = (
        dataframe["total_expense"]
        .fillna(0)
    )

    dataframe["net_profit"] = (
        dataframe["gross_profit"]
        - dataframe["total_expense"]
    )

    dataframe["gross_margin_pct"] = (
        dataframe["gross_profit"]
        / dataframe["revenue"]
        * 100
    )

    dataframe["net_margin_pct"] = (
        dataframe["net_profit"]
        / dataframe["revenue"]
        * 100
    )

    return dataframe


# ============================================================
# OVERALL BUSINESS SUMMARY
# ============================================================

def calculate_business_summary(
    sales_metrics: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate overall business performance metrics."""
    revenue = sales_metrics["net_sales"].sum()
    cogs = sales_metrics["cogs"].sum()
    gross_profit = sales_metrics["gross_profit"].sum()
    operating_expenses = expenses["amount"].sum()
    net_profit = gross_profit - operating_expenses

    gross_margin_pct = (
        gross_profit / revenue * 100
        if revenue
        else 0.0
    )

    net_margin_pct = (
        net_profit / revenue * 100
        if revenue
        else 0.0
    )

    return pd.DataFrame(
        [
            {
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "operating_expenses": operating_expenses,
                "net_profit": net_profit,
                "gross_margin_pct": gross_margin_pct,
                "net_margin_pct": net_margin_pct,
            }
        ]
    )


# ============================================================
# OUTPUT FORMATTING
# ============================================================

def format_currency(value: object) -> str:
    """Format a numeric value as currency-style output."""
    if pd.isna(value):
        return ""

    return f"{float(value):,.2f}"


def format_integer(value: object) -> str:
    """Format a numeric value as an integer."""
    if pd.isna(value):
        return ""

    return f"{int(value):,}"


def format_percentage(value: object) -> str:
    """Format a numeric value as a percentage."""
    if pd.isna(value):
        return ""

    return f"{float(value):.2f}"


def print_dataframe(
    dataframe: pd.DataFrame,
    currency_columns: tuple[str, ...] = (),
    integer_columns: tuple[str, ...] = (),
    percentage_columns: tuple[str, ...] = (),
) -> None:
    """Print a DataFrame with consistent readable formatting."""
    formatters: dict[str, object] = {}

    for column in currency_columns:
        if column in dataframe.columns:
            formatters[column] = format_currency

    for column in integer_columns:
        if column in dataframe.columns:
            formatters[column] = format_integer

    for column in percentage_columns:
        if column in dataframe.columns:
            formatters[column] = format_percentage

    print(
        dataframe.to_string(
            index=False,
            formatters=formatters,
        )
    )


def print_section_title(title: str) -> None:
    """Print a consistent section heading."""
    print(title)
    print("-" * len(title))


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Load datasets and run the complete business analysis."""
    connection = get_connection()

    try:
        datasets = load_all_data(connection)

        summary = summarize_datasets(
            datasets,
        )

        sales_metrics = calculate_sales_metrics(
            datasets["sales"],
            datasets["products"],
        )

        business_summary = calculate_business_summary(
            sales_metrics,
            datasets["expenses"],
        )

        product_performance = calculate_product_performance(
            sales_metrics,
        )

        category_performance = calculate_category_performance(
            sales_metrics,
        )

        payment_performance = calculate_payment_performance(
            sales_metrics,
        )

        customer_segment_performance = (
            calculate_customer_segment_performance(
                datasets["sales"],
                datasets["customers"],
            )
        )

        expense_summary = calculate_expense_summary(
            datasets["expenses"],
        )

        monthly_sales = calculate_monthly_sales(
            sales_metrics,
        )

        monthly_expenses = calculate_monthly_expenses(
            datasets["expenses"],
        )

        monthly_profitability = calculate_monthly_profitability(
            monthly_sales,
            monthly_expenses,
        )

        print("Sasadiakopi analysis completed successfully.")
        print()

        # ----------------------------------------------------
        # DATASET SUMMARY
        # ----------------------------------------------------

        print_section_title("DATASET SUMMARY")

        print_dataframe(
            summary,
            integer_columns=(
                "rows",
                "columns",
            ),
        )

        print()

        # ----------------------------------------------------
        # BUSINESS SUMMARY
        # ----------------------------------------------------

        print_section_title("BUSINESS SUMMARY")

        print_dataframe(
            business_summary,
            currency_columns=(
                "revenue",
                "cogs",
                "gross_profit",
                "operating_expenses",
                "net_profit",
            ),
            percentage_columns=(
                "gross_margin_pct",
                "net_margin_pct",
            ),
        )

        print()

        # ----------------------------------------------------
        # PRODUCT PERFORMANCE
        # ----------------------------------------------------

        print_section_title("PRODUCT PERFORMANCE")

        print_dataframe(
            product_performance,
            currency_columns=(
                "revenue",
                "cogs",
                "gross_profit",
            ),
            integer_columns=(
                "transactions",
                "units_sold",
            ),
            percentage_columns=(
                "gross_margin_pct",
            ),
        )

        print()

        # ----------------------------------------------------
        # CATEGORY PERFORMANCE
        # ----------------------------------------------------

        print_section_title("CATEGORY PERFORMANCE")

        print_dataframe(
            category_performance,
            currency_columns=(
                "revenue",
                "cogs",
                "gross_profit",
            ),
            integer_columns=(
                "transactions",
                "units_sold",
            ),
            percentage_columns=(
                "gross_margin_pct",
            ),
        )

        print()

        # ----------------------------------------------------
        # PAYMENT METHOD PERFORMANCE
        # ----------------------------------------------------

        print_section_title("PAYMENT METHOD PERFORMANCE")

        print_dataframe(
            payment_performance,
            currency_columns=(
                "revenue",
            ),
            integer_columns=(
                "transactions",
                "units_sold",
            ),
        )

        print()

        # ----------------------------------------------------
        # CUSTOMER SEGMENT PERFORMANCE
        # ----------------------------------------------------

        print_section_title("CUSTOMER SEGMENT PERFORMANCE")

        print_dataframe(
            customer_segment_performance,
            currency_columns=(
                "revenue",
            ),
            integer_columns=(
                "transactions",
                "units_sold",
                "unique_customers",
            ),
        )

        print()

        # ----------------------------------------------------
        # EXPENSE SUMMARY
        # ----------------------------------------------------

        print_section_title("EXPENSE SUMMARY")

        print_dataframe(
            expense_summary,
            currency_columns=(
                "total_expense",
            ),
            integer_columns=(
                "expense_count",
            ),
        )

        print()

        # ----------------------------------------------------
        # MONTHLY PROFITABILITY
        # ----------------------------------------------------

        print_section_title("MONTHLY PROFITABILITY")

        print_dataframe(
            monthly_profitability,
            currency_columns=(
                "revenue",
                "cogs",
                "gross_profit",
                "total_expense",
                "net_profit",
            ),
            integer_columns=(
                "transactions",
                "units_sold",
            ),
            percentage_columns=(
                "gross_margin_pct",
                "net_margin_pct",
            ),
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()