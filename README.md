# Sasadiakopi Data Analysis

End-to-end business analytics case study for **Sasadiakopi**, a coffee shop business.

This project demonstrates how raw transactional business data can be transformed into validated datasets, business KPIs, visual analysis, management reports, dashboards, and actionable business insights using **SQL and Python**.

---

## Business Problem

Sasadiakopi needs a structured way to understand its business performance across:

* Revenue
* Product performance
* Product profitability
* Category performance
* Customer segments
* Expenses
* Monthly profitability
* Data quality
* Business risks and opportunities

The goal of this project is to turn operational data into a repeatable analytics workflow that can support management decisions.

---

## Project Objectives

This project was built to answer questions such as:

1. How much revenue and profit does the business generate?
2. Which products generate the most revenue?
3. Which products have the strongest gross margins?
4. Which categories contribute the most revenue?
5. Which categories have weaker margins?
6. Which customer segments generate the most revenue?
7. What are the largest expense categories?
8. Which months perform best and worst?
9. Which months generate losses?
10. Is the source data sufficiently reliable for business analysis?
11. Can the entire analytical workflow be executed consistently through one pipeline?

---

## Dataset

The project uses a SQLite database containing:

* **5,000 sales records**
* **12 products**
* **108 expense records**
* Customer records and customer segments

Core business entities include:

```text
customers
products
sales
expenses
```

The database is accessed through Python and analyzed using Pandas.

---

## Analytics Workflow

```text
                    ┌──────────────────┐
                    │   SQLite Data    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ SQL Analysis     │
                    │ & Data Checks    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Pandas Analysis  │
                    │ & KPI Calculation│
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌─────────────────┐     ┌─────────────────┐
        │ Data Validation │     │ Business Insights│
        └────────┬────────┘     └────────┬────────┘
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    ┌──────────────────┐
                    │ Visualization    │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Report + Dashboard│
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Management Output│
                    └──────────────────┘
```

The complete workflow can be executed through:

```bash
python -m src.pipeline
```

---

## Data Quality Validation

The validation layer performs automated checks across the project datasets.

Current validation checks include:

* Required dataset availability
* Missing values
* Duplicate rows
* Negative numeric values
* Product foreign-key integrity
* Date validity

The current validation run produces:

```text
Checks: 39
Passed: 39
Failed: 0
```

Output:

```text
outputs/validation/sasadiakopi_data_quality.csv
```

---

## Key Business Findings

The current analysis identifies several important business signals.

### Overall profitability

Net profit:

```text
Rp3,571,599
```

Net margin:

```text
2.51%
```

This indicates that the business operates with a relatively thin net margin and therefore has limited room for uncontrolled operating expenses.

### Expense pressure

Rent is currently the largest expense category:

```text
Rp34,633,954
```

This makes rent optimization one of the highest-priority expense management areas.

### Product performance

The highest-revenue product is:

```text
Es Kopi Susu Sasadiakopi
Revenue: Rp28,414,800
```

It also generates the highest gross profit:

```text
Rp15,422,800
```

### Product margin

The product with the highest gross margin is:

```text
Lychee Tea
Gross Margin: 65.90%
```

This indicates a potential opportunity for product promotion and product-mix optimization.

### Category performance

Coffee generates the highest category revenue:

```text
Rp71,460,250
```

Food has the lowest category gross margin:

```text
55.27%
```

This suggests that pricing and cost-of-goods management should be reviewed within the Food category.

### Monthly performance

Weakest month:

```text
2025-02
Net Profit: -Rp989,123
```

Strongest month:

```text
2025-07
Net Profit: Rp2,367,170
```

The analysis also identifies multiple loss-making months requiring further investigation:

```text
2025-02
2025-04
2025-06
2025-10
2025-11
2025-12
```

---

## Business Recommendations

Based on the analysis:

### 1. Control operating expenses

The net margin is below 5%, so operating expense discipline should be prioritized.

### 2. Review rent spending

Rent represents the largest expense category and should be evaluated for optimization opportunities.

### 3. Promote high-margin products

Lychee Tea has the strongest gross margin at 65.90%, making it a candidate for targeted promotion and product-mix optimization.

### 4. Review Food category economics

The Food category has the lowest gross margin at 55.27%.

Pricing, COGS, portion sizes, and product-level profitability should be reviewed.

### 5. Investigate loss-making months

The identified loss-making months should be investigated for changes in:

* Revenue
* Sales volume
* Discounts
* Product mix
* COGS
* Operating expenses

---

## Analytics Outputs

The project generates several analytical artifacts.

### Visualizations

```text
outputs/charts/
```

Includes:

* Monthly revenue and profit
* Monthly net profit
* Product revenue
* Product gross margin
* Category revenue
* Category gross margin
* Payment-method revenue
* Customer-segment revenue
* Expense breakdown

### Business Report

```text
outputs/reports/sasadiakopi_business_report.html
```

### Business Dashboard

```text
outputs/dashboard/sasadiakopi_dashboard.html
```

### Business Insights

```text
outputs/insights/sasadiakopi_insights.csv
```

### Data Quality Report

```text
outputs/validation/sasadiakopi_data_quality.csv
```

Generated outputs are excluded from Git tracking through `.gitignore`.

---

## Project Structure

```text
sasadiakopi-data-analysis/
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_data_quality_checks.sql
│   └── 03_business_analysis.sql
│
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── data_generator.py
│   ├── kpi.py
│   ├── visualization.py
│   ├── report.py
│   ├── dashboard.py
│   ├── insights.py
│   ├── validation.py
│   └── pipeline.py
│
├── tests/
│   └── test_validation.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── sasadiakopi.db
```

---

## Technology Stack

### Data

* SQLite
* SQL

### Analysis

* Python
* Pandas

### Visualization

* Matplotlib

### Reporting

* HTML
* CSV

### Quality & Testing

* Pytest
* Python `compileall`
* Automated data-quality validation

### Development

* Git
* GitHub
* Python virtual environment

---

## Running the Project

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the complete analytics pipeline:

```bash
python -m src.pipeline
```

The pipeline executes:

```text
1. Data validation
2. Business visualization
3. Business report generation
4. Dashboard generation
5. Business insight generation
```

---

## Testing

Run the test suite:

```bash
python -m pytest -q
```

Current test result:

```text
9 passed
```

Compile the project:

```bash
python -m compileall -q src tests
```

Check whitespace errors:

```bash
git diff --check
```

---

## Pipeline Result

The current integrated pipeline successfully completes all five stages:

```text
[PASS] validation
[PASS] visualization
[PASS] report
[PASS] dashboard
[PASS] insights

Pipeline completed successfully: 5 step(s).
```

This makes the project reproducible as an end-to-end analytics workflow rather than a collection of independent analysis scripts.

---

## Skills Demonstrated

This case study demonstrates practical skills in:

* SQL data analysis
* Relational data modeling
* Data quality validation
* Python data analysis
* Pandas
* KPI development
* Business performance analysis
* Profitability analysis
* Customer segmentation
* Expense analysis
* Data visualization
* Dashboard development
* Automated reporting
* Business insights generation
* Automated analytics pipelines
* Unit testing
* Git/GitHub workflow

---

## Business Impact

The main value of this project is not simply producing charts.

The workflow connects:

```text
Data
  ↓
Validation
  ↓
Analysis
  ↓
KPI
  ↓
Visualization
  ↓
Business Insight
  ↓
Decision Support
```

This provides management with a repeatable framework for identifying:

* Profitability problems
* Expense pressure
* Product opportunities
* Margin weaknesses
* Loss-making periods
* Areas requiring deeper investigation

---

## Case Study Summary

**Sasadiakopi Data Analysis** is an end-to-end business analytics case study demonstrating how transactional data can be transformed into actionable management information.

The project combines SQL, Python, Pandas, KPI analysis, visualization, reporting, dashboarding, data-quality validation, automated insights, testing, and pipeline orchestration into a single reproducible workflow.
