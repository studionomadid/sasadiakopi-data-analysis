"""CSV import utilities for the Sasadiakopi data analysis project."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# IMPORT CONTRACTS
# ============================================================

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": (
        "customer_id",
        "customer_name",
        "segment",
        "join_date",
    ),
    "products": (
        "product_id",
        "product_name",
        "category",
        "cost_price",
        "selling_price",
    ),
    "sales": (
        "sale_id",
        "customer_id",
        "product_id",
        "sale_date",
        "quantity",
        "unit_price",
        "discount_pct",
        "payment_method",
    ),
    "expenses": (
        "expense_id",
        "expense_date",
        "category",
        "description",
        "amount",
    ),
}


ID_COLUMNS: dict[str, str] = {
    "customers": "customer_id",
    "products": "product_id",
    "sales": "sale_id",
    "expenses": "expense_id",
}


DATE_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": ("join_date",),
    "products": (),
    "sales": ("sale_date",),
    "expenses": ("expense_date",),
}


NUMERIC_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": (),
    "products": (
        "cost_price",
        "selling_price",
    ),
    "sales": (
        "quantity",
        "unit_price",
        "discount_pct",
    ),
    "expenses": (
        "amount",
    ),
}


# ============================================================
# CSV LOADING
# ============================================================

def load_csv(
    csv_path: str | Path,
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"CSV path is not a file: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# DATASET VALIDATION
# ============================================================

def validate_dataset_name(
    dataset_name: str,
) -> None:
    """Validate that the dataset name is supported."""
    if dataset_name not in REQUIRED_COLUMNS:
        supported = ", ".join(
            sorted(REQUIRED_COLUMNS)
        )

        raise ValueError(
            f"Unsupported dataset '{dataset_name}'. "
            f"Supported datasets: {supported}"
        )


def validate_required_columns(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate that a DataFrame contains all required columns."""
    validate_dataset_name(dataset_name)

    required_columns = set(
        REQUIRED_COLUMNS[dataset_name]
    )

    actual_columns = set(dataframe.columns)

    missing_columns = sorted(
        required_columns - actual_columns
    )

    if missing_columns:
        missing = ", ".join(missing_columns)

        raise ValueError(
            f"Dataset '{dataset_name}' is missing "
            f"required columns: {missing}"
        )


def validate_dataframe(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate the basic import contract for a dataset."""
    validate_dataset_name(dataset_name)

    if dataframe.empty:
        raise ValueError(
            f"Dataset '{dataset_name}' is empty."
        )

    validate_required_columns(
        dataframe,
        dataset_name,
    )


# ============================================================
# ID VALIDATION
# ============================================================

def validate_ids(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate required IDs for missing and duplicate values."""
    validate_dataset_name(dataset_name)

    id_column = ID_COLUMNS[dataset_name]

    if id_column not in dataframe.columns:
        raise ValueError(
            f"Dataset '{dataset_name}' is missing "
            f"ID column '{id_column}'."
        )

    missing_count = int(
        dataframe[id_column].isna().sum()
    )

    if missing_count > 0:
        raise ValueError(
            f"Dataset '{dataset_name}' contains "
            f"{missing_count} missing '{id_column}' values."
        )

    blank_count = int(
        dataframe[id_column]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    if blank_count > 0:
        raise ValueError(
            f"Dataset '{dataset_name}' contains "
            f"{blank_count} blank '{id_column}' values."
        )

    duplicate_count = int(
        dataframe[id_column].duplicated().sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Dataset '{dataset_name}' contains "
            f"{duplicate_count} duplicate '{id_column}' values."
        )


# ============================================================
# DATE VALIDATION
# ============================================================

def validate_dates(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate configured date columns."""
    validate_dataset_name(dataset_name)

    for column in DATE_COLUMNS[dataset_name]:
        if column not in dataframe.columns:
            raise ValueError(
                f"Dataset '{dataset_name}' is missing "
                f"date column '{column}'."
            )

        parsed_dates = pd.to_datetime(
            dataframe[column],
            errors="coerce",
        )

        invalid_count = int(
            parsed_dates.isna().sum()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Dataset '{dataset_name}' contains "
                f"{invalid_count} invalid '{column}' values."
            )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_numeric_columns(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Validate configured numeric columns."""
    validate_dataset_name(dataset_name)

    for column in NUMERIC_COLUMNS[dataset_name]:
        if column not in dataframe.columns:
            raise ValueError(
                f"Dataset '{dataset_name}' is missing "
                f"numeric column '{column}'."
            )

        numeric_values = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        invalid_count = int(
            numeric_values.isna().sum()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Dataset '{dataset_name}' contains "
                f"{invalid_count} invalid numeric "
                f"'{column}' values."
            )


# ============================================================
# FULL IMPORT VALIDATION
# ============================================================

def validate_import(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Run all importer-level validation checks."""
    validate_dataframe(
        dataframe,
        dataset_name,
    )

    validate_ids(
        dataframe,
        dataset_name,
    )

    validate_dates(
        dataframe,
        dataset_name,
    )

    validate_numeric_columns(
        dataframe,
        dataset_name,
    )


# ============================================================
# DATA NORMALIZATION
# ============================================================

def normalize_dataframe(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """Normalize validated data before database insertion."""
    validate_import(
        dataframe,
        dataset_name,
    )

    normalized = dataframe[
        list(REQUIRED_COLUMNS[dataset_name])
    ].copy()

    for column in DATE_COLUMNS[dataset_name]:
        normalized[column] = pd.to_datetime(
            normalized[column],
            errors="raise",
        ).dt.strftime("%Y-%m-%d")

    for column in NUMERIC_COLUMNS[dataset_name]:
        normalized[column] = pd.to_numeric(
            normalized[column],
            errors="raise",
        )

    return normalized


# ============================================================
# DATABASE IMPORT
# ============================================================

def import_dataframe(
    connection: sqlite3.Connection,
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> int:
    """Validate, normalize, and insert a DataFrame into SQLite."""
    validate_dataset_name(dataset_name)

    normalized = normalize_dataframe(
        dataframe,
        dataset_name,
    )

    table_name = dataset_name

    try:
        normalized.to_sql(
            table_name,
            connection,
            if_exists="append",
            index=False,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise

    return len(normalized)


def import_csv(
    connection: sqlite3.Connection,
    csv_path: str | Path,
    dataset_name: str,
) -> int:
    """Load, validate, normalize, and import one CSV file."""
    dataframe = load_csv(csv_path)

    return import_dataframe(
        connection,
        dataframe,
        dataset_name,
    )
