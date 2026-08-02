from __future__ import annotations

from html import escape
from pathlib import Path

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
from src.kpi import (
    calculate_category_kpis,
    calculate_kpi_summary,
    calculate_monthly_kpis,
    calculate_product_kpis,
    calculate_top_product,
    calculate_top_profit_product,
    calculate_best_month,
    calculate_worst_month,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DASHBOARD_DIRECTORY = (
    PROJECT_ROOT / "outputs" / "dashboard"
)

DASHBOARD_PATH = (
    DASHBOARD_DIRECTORY
    / "sasadiakopi_dashboard.html"
)


def format_currency(value: object) -> str:
    """Format a numeric value as Indonesian Rupiah."""
    if pd.isna(value):
        return "Rp0"

    return f"Rp{float(value):,.0f}"


def format_number(value: object) -> str:
    """Format a numeric value."""
    if pd.isna(value):
        return "0"

    return f"{float(value):,.0f}"


def format_percentage(value: object) -> str:
    """Format a percentage value."""
    if pd.isna(value):
        return "0.00%"

    return f"{float(value):.2f}%"


def dataframe_to_html(
    dataframe: pd.DataFrame,
    currency_columns: list[str] | None = None,
    percentage_columns: list[str] | None = None,
) -> str:
    """Convert a dataframe into dashboard-friendly HTML."""
    currency_columns = currency_columns or []
    percentage_columns = percentage_columns or []

    display = dataframe.copy()

    for column in currency_columns:
        if column in display.columns:
            display[column] = display[column].map(
                format_currency
            )

    for column in percentage_columns:
        if column in display.columns:
            display[column] = display[column].map(
                format_percentage
            )

    return display.to_html(
        index=False,
        classes="data-table",
        border=0,
    )


def create_kpi_card(
    title: str,
    value: str,
    description: str,
) -> str:
    """Create a dashboard KPI card."""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">
            {escape(title)}
        </div>

        <div class="kpi-value">
            {escape(value)}
        </div>

        <div class="kpi-description">
            {escape(description)}
        </div>
    </div>
    """


def create_highlight_card(
    title: str,
    value: str,
    description: str,
) -> str:
    """Create a dashboard highlight card."""
    return f"""
    <div class="highlight-card">
        <div class="highlight-title">
            {escape(title)}
        </div>

        <div class="highlight-value">
            {escape(value)}
        </div>

        <div class="highlight-description">
            {escape(description)}
        </div>
    </div>
    """


def create_chart_card(
    title: str,
    filename: str,
) -> str:
    """Create an embedded chart card."""
    chart_path = (
        Path("..")
        / "charts"
        / filename
    )

    return f"""
    <div class="chart-card">
        <h3>
            {escape(title)}
        </h3>

        <img
            src="{escape(chart_path.as_posix())}"
            alt="{escape(title)}"
        >
    </div>
    """


def calculate_dashboard_data() -> dict[str, pd.DataFrame]:
    """Calculate all datasets required by the dashboard."""
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

        product_kpis = calculate_product_kpis(
            product_performance,
        )

        category_kpis = calculate_category_kpis(
            category_performance,
        )

        monthly_kpis = calculate_monthly_kpis(
            monthly_profitability,
        )

        top_product = calculate_top_product(
            product_kpis,
        )

        top_profit_product = calculate_top_profit_product(
            product_kpis,
        )

        best_month = calculate_best_month(
            monthly_kpis,
        )

        worst_month = calculate_worst_month(
            monthly_kpis,
        )

        return {
            "business_summary": business_summary,
            "product_performance": product_performance,
            "category_performance": category_performance,
            "payment_performance": payment_performance,
            "customer_segment_performance": (
                customer_segment_performance
            ),
            "expense_summary": expense_summary,
            "monthly_profitability": monthly_profitability,
            "kpi_summary": kpi_summary,
            "product_kpis": product_kpis,
            "category_kpis": category_kpis,
            "monthly_kpis": monthly_kpis,
            "top_product": top_product.to_frame().T,
            "top_profit_product": (
                top_profit_product.to_frame().T
            ),
            "best_month": best_month.to_frame().T,
            "worst_month": worst_month.to_frame().T,
        }

    finally:
        connection.close()


def build_dashboard_html(
    data: dict[str, pd.DataFrame],
) -> str:
    """Build the complete dashboard HTML."""
    summary = data["business_summary"].iloc[0]
    kpis = data["kpi_summary"].iloc[0]

    top_product = data["top_product"].iloc[0]
    top_profit_product = (
        data["top_profit_product"].iloc[0]
    )
    best_month = data["best_month"].iloc[0]
    worst_month = data["worst_month"].iloc[0]

    report_date = pd.Timestamp.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    kpi_cards = "\n".join(
        [
            create_kpi_card(
                "Revenue",
                format_currency(summary["revenue"]),
                "Total net sales",
            ),
            create_kpi_card(
                "Gross Profit",
                format_currency(summary["gross_profit"]),
                (
                    "Gross margin "
                    f"{format_percentage(summary['gross_margin_pct'])}"
                ),
            ),
            create_kpi_card(
                "Net Profit",
                format_currency(summary["net_profit"]),
                (
                    "Net margin "
                    f"{format_percentage(summary['net_margin_pct'])}"
                ),
            ),
            create_kpi_card(
                "Transactions",
                format_number(kpis["transactions"]),
                "Recorded sales transactions",
            ),
            create_kpi_card(
                "Units Sold",
                format_number(kpis["units_sold"]),
                "Total units sold",
            ),
            create_kpi_card(
                "Average Order Value",
                format_currency(
                    kpis["average_order_value"]
                ),
                "Average revenue per transaction",
            ),
        ]
    )

    highlights = "\n".join(
        [
            create_highlight_card(
                "Top Revenue Product",
                str(top_product["product_name"]),
                format_currency(top_product["revenue"]),
            ),
            create_highlight_card(
                "Top Gross Profit Product",
                str(
                    top_profit_product[
                        "product_name"
                    ]
                ),
                format_currency(
                    top_profit_product["gross_profit"]
                ),
            ),
            create_highlight_card(
                "Best Month",
                str(best_month["month"]),
                format_currency(
                    best_month["net_profit"]
                ),
            ),
            create_highlight_card(
                "Worst Month",
                str(worst_month["month"]),
                format_currency(
                    worst_month["net_profit"]
                ),
            ),
        ]
    )

    charts = "\n".join(
        [
            create_chart_card(
                "Monthly Revenue and Profit",
                "monthly_revenue_and_profit.png",
            ),
            create_chart_card(
                "Monthly Net Profit",
                "monthly_net_profit.png",
            ),
            create_chart_card(
                "Product Revenue",
                "product_revenue.png",
            ),
            create_chart_card(
                "Product Gross Margin",
                "product_gross_margin.png",
            ),
            create_chart_card(
                "Category Revenue",
                "category_revenue.png",
            ),
            create_chart_card(
                "Category Gross Margin",
                "category_gross_margin.png",
            ),
            create_chart_card(
                "Payment Method Revenue",
                "payment_method_revenue.png",
            ),
            create_chart_card(
                "Customer Segment Revenue",
                "customer_segment_revenue.png",
            ),
            create_chart_card(
                "Expense Breakdown",
                "expense_breakdown.png",
            ),
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        Sasadiakopi Business Dashboard
    </title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: #f3f4f6;
            color: #111827;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        .container {{
            max-width: 1500px;
            margin: 0 auto;
            padding: 32px;
        }}

        .header {{
            background: #111827;
            color: white;
            padding: 32px;
            border-radius: 18px;
            margin-bottom: 24px;
        }}

        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 34px;
        }}

        .header p {{
            margin: 4px 0;
            opacity: 0.8;
        }}

        .section {{
            background: white;
            padding: 26px;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow:
                0 4px 20px
                rgba(15, 23, 42, 0.06);
        }}

        .section h2 {{
            margin-top: 0;
            font-size: 24px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(210px, 1fr)
                );
            gap: 16px;
        }}

        .kpi-card {{
            padding: 20px;
            border-radius: 14px;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }}

        .kpi-title {{
            color: #6b7280;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .kpi-value {{
            margin: 8px 0;
            font-size: 25px;
            font-weight: 800;
        }}

        .kpi-description {{
            color: #6b7280;
            font-size: 13px;
        }}

        .highlight-grid {{
            display: grid;
            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(240px, 1fr)
                );
            gap: 16px;
            margin-top: 20px;
        }}

        .highlight-card {{
            padding: 20px;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
        }}

        .highlight-title {{
            color: #6b7280;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .highlight-value {{
            margin-top: 8px;
            font-size: 19px;
            font-weight: 800;
        }}

        .highlight-description {{
            margin-top: 5px;
            color: #4b5563;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(430px, 1fr)
                );
            gap: 20px;
        }}

        .chart-card {{
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            background: white;
        }}

        .chart-card h3 {{
            margin: 0 0 12px 0;
            font-size: 17px;
        }}

        .chart-card img {{
            display: block;
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 700px;
            font-size: 14px;
        }}

        .data-table th {{
            padding: 11px;
            text-align: left;
            background: #f3f4f6;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }}

        .data-table td {{
            padding: 10px 11px;
            border-bottom: 1px solid #e5e7eb;
            white-space: nowrap;
        }}

        .table-wrapper {{
            overflow-x: auto;
        }}

        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 13px;
            padding: 20px;
        }}

        @media (max-width: 700px) {{
            .container {{
                padding: 14px;
            }}

            .header,
            .section {{
                padding: 18px;
            }}

            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media print {{
            body {{
                background: white;
            }}

            .container {{
                max-width: none;
                padding: 0;
            }}

            .section,
            .kpi-card,
            .highlight-card,
            .chart-card {{
                box-shadow: none;
            }}
        }}
    </style>
</head>

<body>

<div class="container">

    <header class="header">

        <h1>
            Sasadiakopi Business Dashboard
        </h1>

        <p>
            Interactive-style management dashboard
            generated from the Sasadiakopi dataset.
        </p>

        <p>
            Generated: {escape(report_date)}
        </p>

    </header>


    <section class="section">

        <h2>
            Executive KPI Dashboard
        </h2>

        <div class="kpi-grid">
            {kpi_cards}
        </div>

        <div class="highlight-grid">
            {highlights}
        </div>

    </section>


    <section class="section">

        <h2>
            Business Visualizations
        </h2>

        <div class="chart-grid">
            {charts}
        </div>

    </section>


    <section class="section">

        <h2>
            Financial Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["business_summary"],
                currency_columns=[
                    "revenue",
                    "cogs",
                    "gross_profit",
                    "operating_expenses",
                    "net_profit",
                ],
                percentage_columns=[
                    "gross_margin_pct",
                    "net_margin_pct",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Product Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["product_kpis"],
                currency_columns=[
                    "revenue",
                    "cogs",
                    "gross_profit",
                    "profit_per_unit",
                ],
                percentage_columns=[
                    "gross_margin_pct",
                    "revenue_contribution_pct",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Category Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["category_kpis"],
                currency_columns=[
                    "revenue",
                    "cogs",
                    "gross_profit",
                    "profit_per_unit",
                ],
                percentage_columns=[
                    "gross_margin_pct",
                    "revenue_contribution_pct",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Payment Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["payment_performance"],
                currency_columns=[
                    "revenue",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Customer Segment Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data[
                    "customer_segment_performance"
                ],
                currency_columns=[
                    "revenue",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Expense Analysis
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["expense_summary"],
                currency_columns=[
                    "total_expense",
                ],
            )}

        </div>

    </section>


    <section class="section">

        <h2>
            Monthly Performance
        </h2>

        <div class="table-wrapper">

            {dataframe_to_html(
                data["monthly_kpis"],
                currency_columns=[
                    "revenue",
                    "cogs",
                    "gross_profit",
                    "total_expense",
                    "net_profit",
                ],
                percentage_columns=[
                    "gross_margin_pct",
                    "net_margin_pct",
                    "revenue_growth_pct",
                    "profit_growth_pct",
                ],
            )}

        </div>

    </section>


    <footer class="footer">

        Sasadiakopi Data Analysis Project

    </footer>

</div>

</body>

</html>
"""


def generate_dashboard() -> Path:
    """Generate the Sasadiakopi HTML dashboard."""
    DASHBOARD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = calculate_dashboard_data()

    html = build_dashboard_html(data)

    DASHBOARD_PATH.write_text(
        html,
        encoding="utf-8",
    )

    return DASHBOARD_PATH


def main() -> None:
    """Generate the Sasadiakopi dashboard."""
    dashboard_path = generate_dashboard()

    print(
        "Sasadiakopi dashboard generated successfully."
    )

    print()

    print(
        f"Dashboard: {dashboard_path}"
    )


if __name__ == "__main__":
    main()
