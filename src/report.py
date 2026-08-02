"""Generate an HTML business report for the Sasadiakopi analysis project."""

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
    calculate_best_month,
    calculate_category_kpis,
    calculate_kpi_summary,
    calculate_monthly_kpis,
    calculate_product_kpis,
    calculate_top_product,
    calculate_top_profit_product,
    calculate_worst_month,
)

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
)

REPORT_PATH = (
    REPORT_DIRECTORY
    / "sasadiakopi_business_report.html"
)


# ============================================================
# FORMATTING HELPERS
# ============================================================

def format_currency(value: float) -> str:
    """Format a numeric value as Indonesian Rupiah."""
    return f"Rp{value:,.0f}".replace(",", ".")


def format_number(value: float) -> str:
    """Format a numeric value using Indonesian separators."""
    return f"{value:,.0f}".replace(",", ".")


def format_decimal(value: float) -> str:
    """Format a numeric value with two decimal places."""
    return (
        f"{value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_percentage(value: float) -> str:
    """Format a percentage value."""
    return f"{value:.2f}%"


def dataframe_to_html(
    dataframe: pd.DataFrame,
    currency_columns: list[str] | None = None,
    percentage_columns: list[str] | None = None,
) -> str:
    """Convert a DataFrame into a readable HTML table."""
    display_dataframe = dataframe.copy()

    currency_columns = currency_columns or []
    percentage_columns = percentage_columns or []

    for column in currency_columns:
        if column in display_dataframe.columns:
            display_dataframe[column] = display_dataframe[column].map(
                format_currency
            )

    for column in percentage_columns:
        if column in display_dataframe.columns:
            display_dataframe[column] = display_dataframe[column].map(
                format_percentage
            )

    for column in display_dataframe.columns:
        if column in currency_columns:
            continue

        if column in percentage_columns:
            continue

        if pd.api.types.is_float_dtype(
            display_dataframe[column]
        ):
            display_dataframe[column] = display_dataframe[column].map(
                format_decimal
            )

    return display_dataframe.to_html(
        index=False,
        border=0,
        classes="data-table",
        justify="left",
    )


# ============================================================
# KPI CARD
# ============================================================

def create_kpi_card(
    title: str,
    value: str,
    description: str,
) -> str:
    """Create one KPI card."""
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


# ============================================================
# BUSINESS FINDINGS
# ============================================================

def generate_business_findings(
    business_summary: pd.DataFrame,
    product_kpis: pd.DataFrame,
    category_kpis: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    expense_summary: pd.DataFrame,
) -> list[str]:
    """Generate concise business findings."""
    summary = business_summary.iloc[0]

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

    top_category = category_kpis.loc[
        category_kpis["revenue"].idxmax()
    ]

    largest_expense = expense_summary.loc[
        expense_summary["total_expense"].idxmax()
    ]

    findings = [
        (
            f"Total revenue reached "
            f"{format_currency(summary['revenue'])}, "
            f"with gross profit of "
            f"{format_currency(summary['gross_profit'])}."
        ),
        (
            f"Net profit was "
            f"{format_currency(summary['net_profit'])}, "
            f"representing a net margin of "
            f"{format_percentage(summary['net_margin_pct'])}."
        ),
        (
            f"{top_product['product_name']} was the top product "
            f"by revenue, generating "
            f"{format_currency(top_product['revenue'])}."
        ),
        (
            f"{top_profit_product['product_name']} generated the "
            f"highest gross profit at "
            f"{format_currency(top_profit_product['gross_profit'])}."
        ),
        (
            f"{top_category['category']} generated the largest "
            f"category revenue at "
            f"{format_currency(top_category['revenue'])}."
        ),
        (
            f"The strongest month was "
            f"{best_month['month']} with net profit of "
            f"{format_currency(best_month['net_profit'])}."
        ),
        (
            f"The weakest month was "
            f"{worst_month['month']} with net profit of "
            f"{format_currency(worst_month['net_profit'])}."
        ),
        (
            f"{largest_expense['category']} was the largest "
            f"operating expense category at "
            f"{format_currency(largest_expense['total_expense'])}."
        ),
    ]

    return findings


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    business_summary: pd.DataFrame,
    product_kpis: pd.DataFrame,
    category_kpis: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    expense_summary: pd.DataFrame,
) -> list[str]:
    """Generate data-driven business recommendations."""
    summary = business_summary.iloc[0]

    recommendations: list[str] = []

    if summary["net_margin_pct"] < 5:
        recommendations.append(
            "Prioritize operating expense control because "
            "the net margin is below 5%."
        )

    highest_margin_product = product_kpis.loc[
        product_kpis["gross_margin_pct"].idxmax()
    ]

    recommendations.append(
        f"Consider promoting "
        f"{highest_margin_product['product_name']} "
        f"because it has the highest gross margin at "
        f"{format_percentage(highest_margin_product['gross_margin_pct'])}."
    )

    lowest_margin_category = category_kpis.loc[
        category_kpis["gross_margin_pct"].idxmin()
    ]

    recommendations.append(
        f"Review pricing and cost structure for the "
        f"{lowest_margin_category['category']} category, "
        f"which has the lowest gross margin at "
        f"{format_percentage(lowest_margin_category['gross_margin_pct'])}."
    )

    largest_expense = expense_summary.loc[
        expense_summary["total_expense"].idxmax()
    ]

    recommendations.append(
        f"Investigate {largest_expense['category']} expenses "
        f"because they represent the largest operating expense "
        f"category."
    )

    loss_months = monthly_kpis[
        monthly_kpis["net_profit"] < 0
    ]

    if not loss_months.empty:
        months = ", ".join(
            loss_months["month"].tolist()
        )

        recommendations.append(
            f"Develop corrective actions for loss-making "
            f"months: {months}."
        )

    recommendations.append(
        "Use monthly revenue and profitability trends as a "
        "recurring management dashboard to identify "
        "deteriorating performance early."
    )

    return recommendations


# ============================================================
# REPORT HTML
# ============================================================

def build_report_html(
    business_summary: pd.DataFrame,
    product_performance: pd.DataFrame,
    category_performance: pd.DataFrame,
    payment_performance: pd.DataFrame,
    customer_segment_performance: pd.DataFrame,
    expense_summary: pd.DataFrame,
    monthly_profitability: pd.DataFrame,
    kpi_summary: pd.DataFrame,
    product_kpis: pd.DataFrame,
    category_kpis: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    findings: list[str],
    recommendations: list[str],
) -> str:
    """Build the complete HTML business report."""
    summary = business_summary.iloc[0]
    kpis = kpi_summary.iloc[0]

    top_revenue_product = calculate_top_product(
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

    report_date = pd.Timestamp.now().strftime(
        "%Y-%m-%d"
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

    findings_html = "\n".join(
        f"<li>{escape(finding)}</li>"
        for finding in findings
    )

    recommendations_html = "\n".join(
        f"<li>{escape(recommendation)}</li>"
        for recommendation in recommendations
    )

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Sasadiakopi Business Report</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            color: #1f2937;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px;
        }}

        .header {{
            background: #111827;
            color: white;
            border-radius: 16px;
            padding: 36px;
            margin-bottom: 28px;
        }}

        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 32px;
        }}

        .header p {{
            margin: 4px 0;
            opacity: 0.85;
        }}

        .section {{
            background: white;
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 28px;
            box-shadow:
                0 4px 18px rgba(15, 23, 42, 0.06);
            overflow-x: auto;
        }}

        .section h2 {{
            margin-top: 0;
            color: #111827;
            font-size: 24px;
        }}

        .section h3 {{
            color: #374151;
            margin-top: 28px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(210px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }}

        .kpi-card {{
            background: white;
            border-radius: 14px;
            padding: 22px;
            box-shadow:
                0 4px 18px rgba(15, 23, 42, 0.06);
        }}

        .kpi-title {{
            color: #6b7280;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .kpi-value {{
            color: #111827;
            font-size: 25px;
            font-weight: 700;
            margin: 8px 0;
        }}

        .kpi-description {{
            color: #6b7280;
            font-size: 13px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 700px;
            font-size: 14px;
        }}

        .data-table th {{
            background: #f3f4f6;
            color: #374151;
            font-weight: 700;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }}

        .data-table td {{
            padding: 11px 12px;
            border-bottom: 1px solid #e5e7eb;
            white-space: nowrap;
        }}

        .data-table tr:hover {{
            background: #f9fafb;
        }}

        .insight-list,
        .recommendation-list {{
            padding-left: 24px;
        }}

        .insight-list li,
        .recommendation-list li {{
            margin-bottom: 12px;
        }}

        .highlight-grid {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
        }}

        .highlight {{
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
        }}

        .highlight-title {{
            color: #6b7280;
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 700;
        }}

        .highlight-value {{
            margin-top: 6px;
            font-size: 19px;
            font-weight: 700;
            color: #111827;
        }}

        .footer {{
            color: #6b7280;
            text-align: center;
            padding: 20px;
            font-size: 13px;
        }}

        @media (max-width: 700px) {{
            .container {{
                padding: 16px;
            }}

            .header,
            .section {{
                padding: 20px;
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
            .kpi-card {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>

<body>

<div class="container">

    <header class="header">

        <h1>
            Sasadiakopi Business Report
        </h1>

        <p>
            Business performance analysis
            and management insights
        </p>

        <p>
            Generated: {escape(report_date)}
        </p>

    </header>


    <section class="section">

        <h2>
            Executive Summary
        </h2>

        <div class="kpi-grid">
            {kpi_cards}
        </div>

        <div class="highlight-grid">

            <div class="highlight">

                <div class="highlight-title">
                    Top Revenue Product
                </div>

                <div class="highlight-value">
                    {escape(
                        top_revenue_product["product_name"]
                    )}
                </div>

                <div>
                    {format_currency(
                        top_revenue_product["revenue"]
                    )}
                </div>

            </div>


            <div class="highlight">

                <div class="highlight-title">
                    Top Gross Profit Product
                </div>

                <div class="highlight-value">
                    {escape(
                        top_profit_product["product_name"]
                    )}
                </div>

                <div>
                    {format_currency(
                        top_profit_product["gross_profit"]
                    )}
                </div>

            </div>


            <div class="highlight">

                <div class="highlight-title">
                    Best Month
                </div>

                <div class="highlight-value">
                    {escape(best_month["month"])}
                </div>

                <div>
                    {format_currency(
                        best_month["net_profit"]
                    )}
                </div>

            </div>


            <div class="highlight">

                <div class="highlight-title">
                    Worst Month
                </div>

                <div class="highlight-value">
                    {escape(worst_month["month"])}
                </div>

                <div>
                    {format_currency(
                        worst_month["net_profit"]
                    )}
                </div>

            </div>

        </div>

    </section>


    <section class="section">

        <h2>
            Financial Performance
        </h2>

        {dataframe_to_html(
            business_summary,
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

    </section>


    <section class="section">

        <h2>
            Product Performance
        </h2>

        {dataframe_to_html(
            product_performance,
            currency_columns=[
                "revenue",
                "cogs",
                "gross_profit",
            ],
            percentage_columns=[
                "gross_margin_pct",
            ],
        )}

        <h3>
            Product KPIs
        </h3>

        {dataframe_to_html(
            product_kpis,
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

    </section>


    <section class="section">

        <h2>
            Category Performance
        </h2>

        {dataframe_to_html(
            category_performance,
            currency_columns=[
                "revenue",
                "cogs",
                "gross_profit",
            ],
            percentage_columns=[
                "gross_margin_pct",
            ],
        )}

        <h3>
            Category KPIs
        </h3>

        {dataframe_to_html(
            category_kpis,
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

    </section>


    <section class="section">

        <h2>
            Payment Performance
        </h2>

        {dataframe_to_html(
            payment_performance,
            currency_columns=[
                "revenue",
            ],
        )}

    </section>


    <section class="section">

        <h2>
            Customer Segment Performance
        </h2>

        {dataframe_to_html(
            customer_segment_performance,
            currency_columns=[
                "revenue",
            ],
        )}

    </section>


    <section class="section">

        <h2>
            Expense Analysis
        </h2>

        {dataframe_to_html(
            expense_summary,
            currency_columns=[
                "total_expense",
            ],
        )}

    </section>


    <section class="section">

        <h2>
            Monthly Profitability
        </h2>

        {dataframe_to_html(
            monthly_profitability,
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
            ],
        )}

        <h3>
            Monthly KPIs
        </h3>

        {dataframe_to_html(
            monthly_kpis,
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

    </section>


    <section class="section">

        <h2>
            Key Business Findings
        </h2>

        <ul class="insight-list">
            {findings_html}
        </ul>

    </section>


    <section class="section">

        <h2>
            Recommendations
        </h2>

        <ul class="recommendation-list">
            {recommendations_html}
        </ul>

    </section>


    <footer class="footer">
        Sasadiakopi Data Analysis Project
    </footer>

</div>

</body>

</html>
"""


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report() -> Path:
    """Generate the complete HTML business report."""
    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = get_connection()

    try:
        datasets = load_all_data(
            connection
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

        findings = generate_business_findings(
            business_summary,
            product_kpis,
            category_kpis,
            monthly_kpis,
            expense_summary,
        )

        recommendations = generate_recommendations(
            business_summary,
            product_kpis,
            category_kpis,
            monthly_kpis,
            expense_summary,
        )

        html = build_report_html(
            business_summary=business_summary,
            product_performance=product_performance,
            category_performance=category_performance,
            payment_performance=payment_performance,
            customer_segment_performance=customer_segment_performance,
            expense_summary=expense_summary,
            monthly_profitability=monthly_profitability,
            kpi_summary=kpi_summary,
            product_kpis=product_kpis,
            category_kpis=category_kpis,
            monthly_kpis=monthly_kpis,
            findings=findings,
            recommendations=recommendations,
        )

        REPORT_PATH.write_text(
            html,
            encoding="utf-8",
        )

        return REPORT_PATH

    finally:
        connection.close()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Generate the Sasadiakopi business report."""
    report_path = generate_report()

    print(
        "Sasadiakopi business report generated successfully."
    )

    print()

    print(
        f"Report: {report_path}"
    )


if __name__ == "__main__":
    main()
