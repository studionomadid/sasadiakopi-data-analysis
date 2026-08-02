from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis import get_connection, load_all_data

OUTPUT_DIRECTORY = Path("outputs/validation")
OUTPUT_PATH = OUTPUT_DIRECTORY / "sasadiakopi_data_quality.csv"


REQUIRED_DATASETS = (
    "sales",
    "products",
    "expenses",
)


def validate_required_datasets(
    datasets: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """Validate that all required datasets are available and non-empty."""
    results: list[dict[str, object]] = []

    for dataset_name in REQUIRED_DATASETS:
        exists = dataset_name in datasets
        row_count = (
            len(datasets[dataset_name])
            if exists
            else 0
        )

        results.append(
            {
                "dataset": dataset_name,
                "check": "required_dataset",
                "status": (
                    "PASS"
                    if exists and row_count > 0
                    else "FAIL"
                ),
                "value": row_count,
                "message": (
                    "Dataset exists and contains rows."
                    if exists and row_count > 0
                    else "Dataset is missing or empty."
                ),
            }
        )

    return results


def validate_missing_values(
    datasets: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """Validate missing values across all datasets."""
    results: list[dict[str, object]] = []

    for dataset_name, dataframe in datasets.items():
        missing_counts = dataframe.isna().sum()

        for column, missing_count in missing_counts.items():
            results.append(
                {
                    "dataset": dataset_name,
                    "check": "missing_values",
                    "status": (
                        "PASS"
                        if missing_count == 0
                        else "FAIL"
                    ),
                    "value": int(missing_count),
                    "message": (
                        f"{column} contains no missing values."
                        if missing_count == 0
                        else (
                            f"{column} contains "
                            f"{missing_count} missing values."
                        )
                    ),
                }
            )

    return results


def validate_duplicates(
    datasets: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """Validate duplicate rows across all datasets."""
    results: list[dict[str, object]] = []

    for dataset_name, dataframe in datasets.items():
        duplicate_count = int(
            dataframe.duplicated().sum()
        )

        results.append(
            {
                "dataset": dataset_name,
                "check": "duplicate_rows",
                "status": (
                    "PASS"
                    if duplicate_count == 0
                    else "FAIL"
                ),
                "value": duplicate_count,
                "message": (
                    "No duplicate rows found."
                    if duplicate_count == 0
                    else (
                        f"{duplicate_count} duplicate rows found."
                    )
                ),
            }
        )

    return results


def validate_numeric_values(
    datasets: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """Validate numeric columns for negative values."""
    results: list[dict[str, object]] = []

    for dataset_name, dataframe in datasets.items():
        numeric_columns = dataframe.select_dtypes(
            include="number"
        ).columns

        for column in numeric_columns:
            negative_count = int(
                (dataframe[column] < 0).sum()
            )

            results.append(
                {
                    "dataset": dataset_name,
                    "check": "negative_numeric_values",
                    "status": (
                        "PASS"
                        if negative_count == 0
                        else "FAIL"
                    ),
                    "value": negative_count,
                    "message": (
                        f"{column} contains no negative values."
                        if negative_count == 0
                        else (
                            f"{column} contains "
                            f"{negative_count} negative values."
                        )
                    ),
                }
            )

    return results


def validate_sales_product_relationship(
    sales: pd.DataFrame,
    products: pd.DataFrame,
) -> list[dict[str, object]]:
    """Validate that sales reference existing products."""
    results: list[dict[str, object]] = []

    if "product_id" not in sales.columns:
        results.append(
            {
                "dataset": "sales",
                "check": "product_foreign_key",
                "status": "FAIL",
                "value": 0,
                "message": "sales.product_id column is missing.",
            }
        )
        return results

    if "product_id" not in products.columns:
        results.append(
            {
                "dataset": "products",
                "check": "product_foreign_key",
                "status": "FAIL",
                "value": 0,
                "message": "products.product_id column is missing.",
            }
        )
        return results

    valid_product_ids = set(
        products["product_id"].dropna()
    )

    invalid_count = int(
        (~sales["product_id"].isin(valid_product_ids)).sum()
    )

    results.append(
        {
            "dataset": "sales",
            "check": "product_foreign_key",
            "status": (
                "PASS"
                if invalid_count == 0
                else "FAIL"
            ),
            "value": invalid_count,
            "message": (
                "All sales reference valid products."
                if invalid_count == 0
                else (
                    f"{invalid_count} sales rows reference "
                    "unknown products."
                )
            ),
        }
    )

    return results


def validate_dates(
    datasets: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """Validate date columns when present."""
    results: list[dict[str, object]] = []

    for dataset_name, dataframe in datasets.items():
        date_columns = [
            column
            for column in dataframe.columns
            if "date" in column.lower()
            or "month" in column.lower()
        ]

        for column in date_columns:
            parsed_dates = pd.to_datetime(
                dataframe[column],
                errors="coerce",
            )

            invalid_count = int(
                parsed_dates.isna().sum()
            )

            results.append(
                {
                    "dataset": dataset_name,
                    "check": "date_validity",
                    "status": (
                        "PASS"
                        if invalid_count == 0
                        else "FAIL"
                    ),
                    "value": invalid_count,
                    "message": (
                        f"{column} contains valid dates."
                        if invalid_count == 0
                        else (
                            f"{column} contains "
                            f"{invalid_count} invalid dates."
                        )
                    ),
                }
            )

    return results


def run_validation(
    datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Run all data-quality validation checks."""
    results: list[dict[str, object]] = []

    results.extend(
        validate_required_datasets(datasets)
    )

    results.extend(
        validate_missing_values(datasets)
    )

    results.extend(
        validate_duplicates(datasets)
    )

    results.extend(
        validate_numeric_values(datasets)
    )

    results.extend(
        validate_sales_product_relationship(
            datasets["sales"],
            datasets["products"],
        )
    )

    results.extend(
        validate_dates(datasets)
    )

    return pd.DataFrame(results)


def save_validation_report(
    validation_results: pd.DataFrame,
) -> Path:
    """Save validation results as CSV."""
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return OUTPUT_PATH


def main() -> None:
    """Run Sasadiakopi data-quality validation."""
    connection = get_connection()

    try:
        datasets = load_all_data(connection)
    finally:
        connection.close()

    validation_results = run_validation(
        datasets
    )

    output_path = save_validation_report(
        validation_results
    )

    passed = int(
        (validation_results["status"] == "PASS").sum()
    )

    failed = int(
        (validation_results["status"] == "FAIL").sum()
    )

    print(
        "Sasadiakopi data validation completed."
    )

    print()

    print(
        f"Checks: {len(validation_results)}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Output: {output_path}"
    )

    print()

    print("VALIDATION RESULTS")
    print("------------------")

    print(
        validation_results[
            [
                "dataset",
                "check",
                "status",
                "value",
                "message",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
