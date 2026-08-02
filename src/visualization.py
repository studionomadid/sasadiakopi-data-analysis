"""Visualization utilities for the Sasadiakopi data analysis project."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis import (
    calculate_category_performance,
    calculate_customer_segment_performance,
    calculate_expense_summary,
    calculate_monthly_expenses,
    calculate_monthly_profitability,
    calculate_monthly_sales,
    calculate_payment_performance,
    calculate_product_performance,
    calculate_sales_metrics,
    get_connection,
    load_all_data,
)

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

def ensure_output_directory() -> None:
    """Create the chart output directory if it does not exist."""
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# CHART STYLE HELPERS
# ============================================================

def save_chart(
    filename: str,
) -> None:
    """Save the current matplotlib figure as a PNG file."""
    path = OUTPUT_DIR / filename

    plt.tight_layout()
    plt.savefig(
        path,
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()


# ============================================================
# 1. MONTHLY REVENUE AND PROFIT
# ============================================================

def plot_monthly_revenue_and_profit(
    monthly_profitability: pd.DataFrame,
) -> None:
    """Plot monthly revenue and net profit."""
    dataframe = monthly_profitability.copy()

    _figure, axis = plt.subplots(
        figsize=(12, 6),
    )

    axis.plot(
        dataframe["month"],
        dataframe["revenue"],
        marker="o",
        label="Revenue",
    )

    axis.plot(
        dataframe["month"],
        dataframe["net_profit"],
        marker="o",
        label="Net Profit",
    )

    axis.axhline(
        0,
        linewidth=1,
    )

    axis.set_title(
        "Monthly Revenue and Net Profit",
    )
    axis.set_xlabel("Month")
    axis.set_ylabel("Amount (Rp)")

    axis.tick_params(
        axis="x",
        rotation=45,
    )

    axis.legend()

    save_chart(
        "monthly_revenue_and_profit.png",
    )


# ============================================================
# 2. PRODUCT REVENUE
# ============================================================

def plot_product_revenue(
    product_performance: pd.DataFrame,
) -> None:
    """Plot revenue by product."""
    dataframe = (
        product_performance
        .sort_values(
            "revenue",
            ascending=True,
        )
    )

    _figure, axis = plt.subplots(
        figsize=(10, 7),
    )

    axis.barh(
        dataframe["product_name"],
        dataframe["revenue"],
    )

    axis.set_title(
        "Revenue by Product",
    )
    axis.set_xlabel("Revenue (Rp)")
    axis.set_ylabel("Product")

    save_chart(
        "product_revenue.png",
    )


# ============================================================
# 3. PRODUCT GROSS MARGIN
# ============================================================

def plot_product_gross_margin(
    product_performance: pd.DataFrame,
) -> None:
    """Plot gross margin percentage by product."""
    dataframe = (
        product_performance
        .sort_values(
            "gross_margin_pct",
            ascending=True,
        )
    )

    _figure, axis = plt.subplots(
        figsize=(10, 7),
    )

    axis.barh(
        dataframe["product_name"],
        dataframe["gross_margin_pct"],
    )

    axis.set_title(
        "Gross Margin by Product",
    )
    axis.set_xlabel("Gross Margin (%)")
    axis.set_ylabel("Product")

    save_chart(
        "product_gross_margin.png",
    )


# ============================================================
# 4. CATEGORY REVENUE
# ============================================================

def plot_category_revenue(
    category_performance: pd.DataFrame,
) -> None:
    """Plot revenue by product category."""
    _figure, axis = plt.subplots(
        figsize=(8, 6),
    )

    axis.bar(
        category_performance["category"],
        category_performance["revenue"],
    )

    axis.set_title(
        "Revenue by Category",
    )
    axis.set_xlabel("Category")
    axis.set_ylabel("Revenue (Rp)")

    save_chart(
        "category_revenue.png",
    )


# ============================================================
# 5. PAYMENT METHOD
# ============================================================

def plot_payment_revenue(
    payment_performance: pd.DataFrame,
) -> None:
    """Plot revenue by payment method."""
    _figure, axis = plt.subplots(
        figsize=(8, 6),
    )

    axis.bar(
        payment_performance["payment_method"],
        payment_performance["revenue"],
    )

    axis.set_title(
        "Revenue by Payment Method",
    )
    axis.set_xlabel("Payment Method")
    axis.set_ylabel("Revenue (Rp)")

    save_chart(
        "payment_method_revenue.png",
    )


# ============================================================
# 6. CUSTOMER SEGMENT
# ============================================================

def plot_customer_segment_revenue(
    customer_segment_performance: pd.DataFrame,
) -> None:
    """Plot revenue by customer segment."""
    _figure, axis = plt.subplots(
        figsize=(8, 6),
    )

    axis.bar(
        customer_segment_performance["segment"],
        customer_segment_performance["revenue"],
    )

    axis.set_title(
        "Revenue by Customer Segment",
    )
    axis.set_xlabel("Customer Segment")
    axis.set_ylabel("Revenue (Rp)")

    save_chart(
        "customer_segment_revenue.png",
    )


# ============================================================
# 7. EXPENSE BREAKDOWN
# ============================================================

def plot_expense_breakdown(
    expense_summary: pd.DataFrame,
) -> None:
    """Plot operating expenses by category."""
    dataframe = (
        expense_summary
        .sort_values(
            "total_expense",
            ascending=True,
        )
    )

    _figure, axis = plt.subplots(
        figsize=(10, 7),
    )

    axis.barh(
        dataframe["category"],
        dataframe["total_expense"],
    )

    axis.set_title(
        "Operating Expenses by Category",
    )
    axis.set_xlabel("Expense (Rp)")
    axis.set_ylabel("Expense Category")

    save_chart(
        "expense_breakdown.png",
    )


# ============================================================
# 8. MONTHLY NET PROFIT
# ============================================================

def plot_monthly_net_profit(
    monthly_profitability: pd.DataFrame,
) -> None:
    """Plot monthly net profit."""
    dataframe = monthly_profitability.copy()

    _figure, axis = plt.subplots(
        figsize=(12, 6),
    )

    axis.bar(
        dataframe["month"],
        dataframe["net_profit"],
    )

    axis.axhline(
        0,
        linewidth=1,
    )

    axis.set_title(
        "Monthly Net Profit",
    )
    axis.set_xlabel("Month")
    axis.set_ylabel("Net Profit (Rp)")

    axis.tick_params(
        axis="x",
        rotation=45,
    )

    save_chart(
        "monthly_net_profit.png",
    )


# ============================================================
# 9. CATEGORY GROSS MARGIN
# ============================================================

def plot_category_gross_margin(
    category_performance: pd.DataFrame,
) -> None:
    """Plot gross margin percentage by category."""
    _figure, axis = plt.subplots(
        figsize=(8, 6),
    )

    axis.bar(
        category_performance["category"],
        category_performance["gross_margin_pct"],
    )

    axis.set_title(
        "Gross Margin by Category",
    )
    axis.set_xlabel("Category")
    axis.set_ylabel("Gross Margin (%)")

    save_chart(
        "category_gross_margin.png",
    )


# ============================================================
# VISUALIZATION PIPELINE
# ============================================================

def generate_all_charts(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Generate all project visualization outputs."""
    ensure_output_directory()

    sales_metrics = calculate_sales_metrics(
        datasets["sales"],
        datasets["products"],
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

    plot_monthly_revenue_and_profit(
        monthly_profitability,
    )

    plot_product_revenue(
        product_performance,
    )

    plot_product_gross_margin(
        product_performance,
    )

    plot_category_revenue(
        category_performance,
    )

    plot_payment_revenue(
        payment_performance,
    )

    plot_customer_segment_revenue(
        customer_segment_performance,
    )

    plot_expense_breakdown(
        expense_summary,
    )

    plot_monthly_net_profit(
        monthly_profitability,
    )

    plot_category_gross_margin(
        category_performance,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Load data and generate all business analysis charts."""
    connection = get_connection()

    try:
        datasets = load_all_data(
            connection,
        )

        generate_all_charts(
            datasets,
        )

    finally:
        connection.close()

    chart_count = len(
        list(
            OUTPUT_DIR.glob("*.png"),
        )
    )

    print(
        "Sasadiakopi visualization completed successfully."
    )
    print()
    print(
        f"Charts generated: {chart_count}"
    )
    print(
        f"Output directory: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
