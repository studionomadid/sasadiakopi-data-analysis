from __future__ import annotations

import pandas as pd

from src.validation import (
    validate_dates,
    validate_duplicates,
    validate_missing_values,
    validate_numeric_values,
    validate_required_datasets,
    validate_sales_product_relationship,
)


def test_validate_required_datasets_passes_for_valid_data() -> None:
    datasets = {
        "sales": pd.DataFrame({"sale_id": [1, 2]}),
        "products": pd.DataFrame({"product_id": [1]}),
        "expenses": pd.DataFrame({"amount": [1000]}),
    }

    results = validate_required_datasets(datasets)

    assert len(results) == 3
    assert all(result["status"] == "PASS" for result in results)


def test_validate_required_datasets_fails_for_missing_dataset() -> None:
    datasets = {
        "sales": pd.DataFrame({"sale_id": [1]}),
        "products": pd.DataFrame({"product_id": [1]}),
    }

    results = validate_required_datasets(datasets)

    expenses_result = next(
        result
        for result in results
        if result["dataset"] == "expenses"
    )

    assert expenses_result["status"] == "FAIL"


def test_validate_missing_values_detects_nulls() -> None:
    datasets = {
        "sales": pd.DataFrame(
            {
                "sale_id": [1, 2],
                "quantity": [2, None],
            }
        )
    }

    results = validate_missing_values(datasets)

    quantity_result = next(
        result
        for result in results
        if result["dataset"] == "sales"
        and result["check"] == "missing_values"
        and "quantity" in str(result["message"])
    )

    assert quantity_result["status"] == "FAIL"
    assert quantity_result["value"] == 1


def test_validate_duplicates_detects_duplicate_rows() -> None:
    datasets = {
        "sales": pd.DataFrame(
            {
                "sale_id": [1, 1],
                "quantity": [2, 2],
            }
        )
    }

    results = validate_duplicates(datasets)

    assert results[0]["status"] == "FAIL"
    assert results[0]["value"] == 1


def test_validate_numeric_values_detects_negative_values() -> None:
    datasets = {
        "sales": pd.DataFrame(
            {
                "quantity": [2, -1],
                "unit_price": [10000, 15000],
            }
        )
    }

    results = validate_numeric_values(datasets)

    quantity_result = next(
        result
        for result in results
        if result["dataset"] == "sales"
        and result["value"] == 1
    )

    assert quantity_result["status"] == "FAIL"
    assert quantity_result["value"] == 1


def test_validate_sales_product_relationship_passes_for_valid_ids() -> None:
    sales = pd.DataFrame(
        {
            "product_id": [1, 2, 1],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": [1, 2],
        }
    )

    results = validate_sales_product_relationship(
        sales,
        products,
    )

    assert results[0]["status"] == "PASS"
    assert results[0]["value"] == 0


def test_validate_sales_product_relationship_detects_invalid_ids() -> None:
    sales = pd.DataFrame(
        {
            "product_id": [1, 2, 999],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": [1, 2],
        }
    )

    results = validate_sales_product_relationship(
        sales,
        products,
    )

    assert results[0]["status"] == "FAIL"
    assert results[0]["value"] == 1


def test_validate_dates_passes_for_valid_dates() -> None:
    datasets = {
        "sales": pd.DataFrame(
            {
                "sale_date": [
                    "2025-01-01",
                    "2025-02-01",
                ]
            }
        )
    }

    results = validate_dates(datasets)

    assert results[0]["status"] == "PASS"
    assert results[0]["value"] == 0


def test_validate_dates_detects_invalid_dates() -> None:
    datasets = {
        "sales": pd.DataFrame(
            {
                "sale_date": [
                    "2025-01-01",
                    "not-a-date",
                ]
            }
        )
    }

    results = validate_dates(datasets)

    assert results[0]["status"] == "FAIL"
    assert results[0]["value"] == 1
