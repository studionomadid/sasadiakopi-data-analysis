from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis import (
    calculate_business_summary,
    calculate_category_performance,
    calculate_expense_summary,
    calculate_monthly_expenses,
    calculate_monthly_profitability,
    calculate_monthly_sales,
    calculate_product_performance,
    calculate_sales_metrics,
    get_connection,
    load_all_data,
)
from src.kpi import (
    calculate_best_month,
    calculate_category_kpis,
    calculate_product_kpis,
    calculate_worst_month,
)

OUTPUT_DIRECTORY = Path("outputs/insights")
OUTPUT_PATH = OUTPUT_DIRECTORY / "sasadiakopi_insights.csv"


def format_currency(value: object) -> str:
    """Format a numeric value as Indonesian Rupiah."""
    if pd.isna(value):
        return "Rp0"

    return f"Rp{float(value):,.0f}"


def format_percentage(value: object) -> str:
    """Format a numeric value as a percentage."""
    if pd.isna(value):
        return "0.00%"

    return f"{float(value):.2f}%"


def generate_business_findings(
    business_summary: pd.DataFrame,
    product_kpis: pd.DataFrame,
    category_kpis: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    expense_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Generate structured business findings."""
    summary = business_summary.iloc[0]

    top_product = product_kpis.loc[
        product_kpis["revenue"].idxmax()
    ]

    top_profit_product = product_kpis.loc[
        product_kpis["gross_profit"].idxmax()
    ]

    top_margin_product = product_kpis.loc[
        product_kpis["gross_margin_pct"].idxmax()
    ]

    top_category = category_kpis.loc[
        category_kpis["revenue"].idxmax()
    ]

    lowest_margin_category = category_kpis.loc[
        category_kpis["gross_margin_pct"].idxmin()
    ]

    best_month = calculate_best_month(monthly_kpis)
    worst_month = calculate_worst_month(monthly_kpis)

    largest_expense = expense_summary.loc[
        expense_summary["total_expense"].idxmax()
    ]

    findings: list[dict[str, object]] = [
        {
            "priority": "HIGH",
            "area": "Profitability",
            "finding": (
                f"Net profit is {format_currency(summary['net_profit'])} "
                f"with a net margin of "
                f"{format_percentage(summary['net_margin_pct'])}."
            ),
            "metric": float(summary["net_margin_pct"]),
            "metric_name": "net_margin_pct",
        },
        {
            "priority": "HIGH",
            "area": "Expense",
            "finding": (
                f"{largest_expense['category']} is the largest expense "
                f"category at "
                f"{format_currency(largest_expense['total_expense'])}."
            ),
            "metric": float(largest_expense["total_expense"]),
            "metric_name": "total_expense",
        },
        {
            "priority": "HIGH",
            "area": "Monthly Performance",
            "finding": (
                f"{worst_month['month']} is the weakest month with "
                f"net profit of "
                f"{format_currency(worst_month['net_profit'])}."
            ),
            "metric": float(worst_month["net_profit"]),
            "metric_name": "net_profit",
        },
        {
            "priority": "MEDIUM",
            "area": "Product",
            "finding": (
                f"{top_product['product_name']} generates the highest "
                f"revenue at "
                f"{format_currency(top_product['revenue'])}."
            ),
            "metric": float(top_product["revenue"]),
            "metric_name": "revenue",
        },
        {
            "priority": "MEDIUM",
            "area": "Product Profitability",
            "finding": (
                f"{top_profit_product['product_name']} generates the "
                f"highest gross profit at "
                f"{format_currency(top_profit_product['gross_profit'])}."
            ),
            "metric": float(top_profit_product["gross_profit"]),
            "metric_name": "gross_profit",
        },
        {
            "priority": "MEDIUM",
            "area": "Product Margin",
            "finding": (
                f"{top_margin_product['product_name']} has the highest "
                f"gross margin at "
                f"{format_percentage(top_margin_product['gross_margin_pct'])}."
            ),
            "metric": float(top_margin_product["gross_margin_pct"]),
            "metric_name": "gross_margin_pct",
        },
        {
            "priority": "MEDIUM",
            "area": "Category",
            "finding": (
                f"{top_category['category']} contributes the highest "
                f"category revenue at "
                f"{format_currency(top_category['revenue'])}."
            ),
            "metric": float(top_category["revenue"]),
            "metric_name": "revenue",
        },
        {
            "priority": "MEDIUM",
            "area": "Category Margin",
            "finding": (
                f"{lowest_margin_category['category']} has the lowest "
                f"category gross margin at "
                f"{format_percentage(lowest_margin_category['gross_margin_pct'])}."
            ),
            "metric": float(
                lowest_margin_category["gross_margin_pct"]
            ),
            "metric_name": "gross_margin_pct",
        },
        {
            "priority": "MEDIUM",
            "area": "Monthly Performance",
            "finding": (
                f"{best_month['month']} is the strongest month with "
                f"net profit of "
                f"{format_currency(best_month['net_profit'])}."
            ),
            "metric": float(best_month["net_profit"]),
            "metric_name": "net_profit",
        },
    ]

    return pd.DataFrame(findings)


def generate_recommendations(
    business_summary: pd.DataFrame,
    product_kpis: pd.DataFrame,
    category_kpis: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    expense_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Generate structured, data-driven recommendations."""
    summary = business_summary.iloc[0]

    recommendations: list[dict[str, object]] = []

    if summary["net_margin_pct"] < 5:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Profitability",
                "recommendation": (
                    "Prioritize operating expense control because "
                    "net margin is below 5%."
                ),
                "expected_impact": "Improve net profitability",
            }
        )

    largest_expense = expense_summary.loc[
        expense_summary["total_expense"].idxmax()
    ]

    recommendations.append(
        {
            "priority": "HIGH",
            "area": "Expense Control",
            "recommendation": (
                f"Review {largest_expense['category']} spending and "
                "identify opportunities to reduce or optimize costs."
            ),
            "expected_impact": "Reduce operating expense pressure",
        }
    )

    highest_margin_product = product_kpis.loc[
        product_kpis["gross_margin_pct"].idxmax()
    ]

    recommendations.append(
        {
            "priority": "MEDIUM",
            "area": "Product Strategy",
            "recommendation": (
                f"Consider promoting "
                f"{highest_margin_product['product_name']} because it "
                f"has the highest gross margin at "
                f"{format_percentage(highest_margin_product['gross_margin_pct'])}."
            ),
            "expected_impact": "Increase contribution from high-margin products",
        }
    )

    lowest_margin_category = category_kpis.loc[
        category_kpis["gross_margin_pct"].idxmin()
    ]

    recommendations.append(
        {
            "priority": "MEDIUM",
            "area": "Category Strategy",
            "recommendation": (
                f"Review pricing and COGS for the "
                f"{lowest_margin_category['category']} category because "
                f"its gross margin is only "
                f"{format_percentage(lowest_margin_category['gross_margin_pct'])}."
            ),
            "expected_impact": "Improve category-level profitability",
        }
    )

    loss_months = monthly_kpis[
        monthly_kpis["net_profit"] < 0
    ]

    if not loss_months.empty:
        months = ", ".join(
            loss_months["month"].astype(str).tolist()
        )

        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Monthly Performance",
                "recommendation": (
                    f"Investigate the loss-making months: {months}."
                ),
                "expected_impact": "Reduce recurring monthly losses",
            }
        )

    recommendations.append(
        {
            "priority": "LOW",
            "area": "Management",
            "recommendation": (
                "Use the KPI, visualization, report, dashboard, and "
                "insight layers as a recurring management review."
            ),
            "expected_impact": "Improve decision-making consistency",
        }
    )

    return pd.DataFrame(recommendations)


def generate_insights() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate findings and recommendations from source data."""
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

        product_kpis = calculate_product_kpis(
            product_performance,
        )

        category_kpis = calculate_category_kpis(
            category_performance,
        )

        monthly_kpis = (
            monthly_profitability
            .copy()
        )

        findings = generate_business_findings(
            business_summary,
            product_kpis,
            category_kpis,
            monthly_kpis,
            calculate_expense_summary(
                datasets["expenses"],
            ),
        )

        recommendations = generate_recommendations(
            business_summary,
            product_kpis,
            category_kpis,
            monthly_kpis,
            calculate_expense_summary(
                datasets["expenses"],
            ),
        )

        return findings, recommendations

    finally:
        connection.close()


def save_insights(
    findings: pd.DataFrame,
    recommendations: pd.DataFrame,
) -> Path:
    """Save generated insights as a CSV dataset."""
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    findings_output = findings.copy()
    findings_output["type"] = "finding"

    recommendations_output = recommendations.copy()
    recommendations_output["type"] = "recommendation"

    recommendations_output = recommendations_output.rename(
        columns={
            "recommendation": "finding",
        }
    )

    combined = pd.concat(
        [
            findings_output[
                [
                    "type",
                    "priority",
                    "area",
                    "finding",
                    "metric",
                    "metric_name",
                ]
            ],
            recommendations_output.assign(
                metric=pd.NA,
                metric_name=pd.NA,
            )[
                [
                    "type",
                    "priority",
                    "area",
                    "finding",
                    "metric",
                    "metric_name",
                ]
            ],
        ],
        ignore_index=True,
    )

    combined.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return OUTPUT_PATH


def main() -> None:
    """Generate and save Sasadiakopi business insights."""
    findings, recommendations = generate_insights()

    output_path = save_insights(
        findings,
        recommendations,
    )

    print(
        "Sasadiakopi insights generated successfully."
    )

    print()

    print(
        f"Findings: {len(findings)}"
    )

    print(
        f"Recommendations: {len(recommendations)}"
    )

    print(
        f"Output: {output_path}"
    )

    print()

    print("FINDINGS")
    print("--------")
    print(
        findings[
            [
                "priority",
                "area",
                "finding",
            ]
        ].to_string(index=False)
    )

    print()

    print("RECOMMENDATIONS")
    print("---------------")
    print(
        recommendations[
            [
                "priority",
                "area",
                "recommendation",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
