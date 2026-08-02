"""Business KPI calculations for the Sasadiakopi data analysis project."""

from __future__ import annotations

import pandas as pd

from src.analysis import (
    calculate_business_summary,
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
# KPI CALCULATIONS
# ============================================================

def calculate_average_order_value(
    sales_metrics: pd.DataFrame,
) -> float:
    """Calculate average revenue per transaction."""
    transaction_count = sales_metrics["sale_id"].nunique()

    if transaction_count == 0:
        return 0.0

    return float(
        sales_metrics["net_sales"].sum()
        / transaction_count
    )


def calculate_average_units_per_transaction(
    sales_metrics: pd.DataFrame,
) -> float:
    """Calculate average units sold per transaction."""
    transaction_count = sales_metrics["sale_id"].nunique()

    if transaction_count == 0:
        return 0.0

    return float(
        sales_metrics["quantity"].sum()
        / transaction_count
    )


def calculate_cogs_ratio(
    business_summary: pd.DataFrame,
) -> float:
    """Calculate COGS as a percentage of revenue."""
    revenue = float(business_summary.loc[0, "revenue"])
    cogs = float(business_summary.loc[0, "cogs"])

    if revenue == 0:
        return 0.0

    return cogs / revenue * 100


def calculate_operating_expense_ratio(
    business_summary: pd.DataFrame,
) -> float:
    """Calculate operating expenses as a percentage of revenue."""
    revenue = float(business_summary.loc[0, "revenue"])
    expenses = float(
        business_summary.loc[0, "operating_expenses"]
    )

    if revenue == 0:
        return 0.0

    return expenses / revenue * 100


def calculate_profitability_rate(
    business_summary: pd.DataFrame,
) -> float:
    """Calculate net profit as a percentage of gross profit."""
    gross_profit = float(
        business_summary.loc[0, "gross_profit"]
    )
    net_profit = float(
        business_summary.loc[0, "net_profit"]
    )

    if gross_profit == 0:
        return 0.0

    return net_profit / gross_profit * 100


def calculate_revenue_contribution(
    dataframe: pd.DataFrame,
    revenue_column: str = "revenue",
) -> pd.DataFrame:
    """Calculate revenue contribution percentage."""
    result = dataframe.copy()

    total_revenue = result[revenue_column].sum()

    if total_revenue == 0:
        result["revenue_contribution_pct"] = 0.0
    else:
        result["revenue_contribution_pct"] = (
            result[revenue_column]
            / total_revenue
            * 100
        )

    return result


def calculate_top_product(
    product_performance: pd.DataFrame,
) -> pd.Series:
    """Return the highest-revenue product."""
    if product_performance.empty:
        return pd.Series(dtype=object)

    return product_performance.iloc[0]


def calculate_top_profit_product(
    product_performance: pd.DataFrame,
) -> pd.Series:
    """Return the highest-gross-profit product."""
    if product_performance.empty:
        return pd.Series(dtype=object)

    return (
        product_performance
        .sort_values(
            "gross_profit",
            ascending=False,
        )
        .iloc[0]
    )


def calculate_best_month(
    monthly_profitability: pd.DataFrame,
) -> pd.Series:
    """Return the month with the highest net profit."""
    if monthly_profitability.empty:
        return pd.Series(dtype=object)

    return (
        monthly_profitability
        .sort_values(
            "net_profit",
            ascending=False,
        )
        .iloc[0]
    )


def calculate_worst_month(
    monthly_profitability: pd.DataFrame,
) -> pd.Series:
    """Return the month with the lowest net profit."""
    if monthly_profitability.empty:
        return pd.Series(dtype=object)

    return (
        monthly_profitability
        .sort_values(
            "net_profit",
            ascending=True,
        )
        .iloc[0]
    )


def calculate_kpi_summary(
    sales_metrics: pd.DataFrame,
    business_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the primary business KPI summary."""
    revenue = float(
        business_summary.loc[0, "revenue"]
    )
    gross_profit = float(
        business_summary.loc[0, "gross_profit"]
    )
    net_profit = float(
        business_summary.loc[0, "net_profit"]
    )

    return pd.DataFrame(
        [
            {
                "revenue": revenue,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "transactions": sales_metrics[
                    "sale_id"
                ].nunique(),
                "units_sold": int(
                    sales_metrics["quantity"].sum()
                ),
                "average_order_value": (
                    calculate_average_order_value(
                        sales_metrics
                    )
                ),
                "average_units_per_transaction": (
                    calculate_average_units_per_transaction(
                        sales_metrics
                    )
                ),
                "cogs_ratio_pct": (
                    calculate_cogs_ratio(
                        business_summary
                    )
                ),
                "operating_expense_ratio_pct": (
                    calculate_operating_expense_ratio(
                        business_summary
                    )
                ),
                "gross_margin_pct": (
                    float(
                        business_summary.loc[
                            0,
                            "gross_margin_pct",
                        ]
                    )
                ),
                "net_margin_pct": (
                    float(
                        business_summary.loc[
                            0,
                            "net_margin_pct",
                        ]
                    )
                ),
                "profitability_rate_pct": (
                    calculate_profitability_rate(
                        business_summary
                    )
                ),
            }
        ]
    )


def calculate_category_kpis(
    category_performance: pd.DataFrame,
) -> pd.DataFrame:
    """Add KPI metrics to category performance."""
    result = calculate_revenue_contribution(
        category_performance
    )

    result["profit_per_unit"] = (
        result["gross_profit"]
        / result["units_sold"]
    )

    return result.sort_values(
        "revenue",
        ascending=False,
    )


def calculate_product_kpis(
    product_performance: pd.DataFrame,
) -> pd.DataFrame:
    """Add KPI metrics to product performance."""
    result = calculate_revenue_contribution(
        product_performance
    )

    result["profit_per_unit"] = (
        result["gross_profit"]
        / result["units_sold"]
    )

    return result.sort_values(
        "revenue",
        ascending=False,
    )


def calculate_monthly_kpis(
    monthly_profitability: pd.DataFrame,
) -> pd.DataFrame:
    """Add KPI metrics to monthly profitability."""
    result = monthly_profitability.copy()

    result["revenue_growth_pct"] = (
        result["revenue"]
        .pct_change()
        .mul(100)
        .fillna(0)
    )

    result["profit_growth_pct"] = (
        result["net_profit"]
        .pct_change()
        .mul(100)
        .fillna(0)
    )

    return result


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run the complete KPI analysis."""
    connection = get_connection()

    try:
        datasets = load_all_data(connection)

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

        monthly_profitability = (
            calculate_monthly_profitability(
                monthly_sales,
                monthly_expenses,
            )
        )

        kpi_summary = calculate_kpi_summary(
            sales_metrics,
            business_summary,
        )

        category_kpis = calculate_category_kpis(
            category_performance,
        )

        product_kpis = calculate_product_kpis(
            product_performance,
        )

        monthly_kpis = calculate_monthly_kpis(
            monthly_profitability,
        )

        top_product = calculate_top_product(
            product_performance,
        )

        top_profit_product = calculate_top_profit_product(
            product_performance,
        )

        best_month = calculate_best_month(
            monthly_profitability,
        )

        worst_month = calculate_worst_month(
            monthly_profitability,
        )

        print("Sasadiakopi KPI analysis completed successfully.")
        print()

        print("KPI SUMMARY")
        print("-----------")
        print(
            kpi_summary.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("TOP REVENUE PRODUCT")
        print("-------------------")
        print(
            f"{top_product['product_name']} "
            f"| Revenue: "
            f"Rp{top_product['revenue']:,.0f}"
        )

        print()
        print("TOP GROSS PROFIT PRODUCT")
        print("------------------------")
        print(
            f"{top_profit_product['product_name']} "
            f"| Gross Profit: "
            f"Rp{top_profit_product['gross_profit']:,.0f}"
        )

        print()
        print("BEST MONTH")
        print("----------")
        print(
            f"{best_month['month']} "
            f"| Net Profit: "
            f"Rp{best_month['net_profit']:,.0f}"
        )

        print()
        print("WORST MONTH")
        print("-----------")
        print(
            f"{worst_month['month']} "
            f"| Net Profit: "
            f"Rp{worst_month['net_profit']:,.0f}"
        )

        print()
        print("CATEGORY KPIs")
        print("-------------")
        print(
            category_kpis.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("PRODUCT KPIs")
        print("------------")
        print(
            product_kpis.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("PAYMENT PERFORMANCE")
        print("-------------------")
        print(
            payment_performance.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("CUSTOMER SEGMENT PERFORMANCE")
        print("----------------------------")
        print(
            customer_segment_performance.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("EXPENSE SUMMARY")
        print("---------------")
        print(
            expense_summary.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

        print()
        print("MONTHLY KPIs")
        print("------------")
        print(
            monthly_kpis.to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()
