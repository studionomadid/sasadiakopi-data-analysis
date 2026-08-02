from __future__ import annotations

import sqlite3

import pandas as pd
from pandas.errors import DatabaseError
import pytest

from src.importer import (
    import_csv,
    import_dataframe,
    load_csv,
    normalize_dataframe,
    validate_dataframe,
    validate_dates,
    validate_dataset_name,
    validate_ids,
    validate_import,
    validate_numeric_columns,
    validate_required_columns,
)


def create_test_database() -> sqlite3.Connection:
    """Create a minimal SQLite database for importer tests."""
    connection = sqlite3.connect(":memory:")

    connection.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            segment TEXT NOT NULL,
            join_date TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            cost_price INTEGER NOT NULL,
            selling_price INTEGER NOT NULL
        );

        CREATE TABLE sales (
            sale_id TEXT PRIMARY KEY,
            customer_id TEXT,
            product_id TEXT NOT NULL,
            sale_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            discount_pct REAL NOT NULL,
            payment_method TEXT NOT NULL
        );

        CREATE TABLE expenses (
            expense_id TEXT PRIMARY KEY,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL
        );
        """
    )

    return connection


def customer_dataframe() -> pd.DataFrame:
    """Return valid customer test data."""
    return pd.DataFrame(
        {
            "customer_id": [
                "C0001",
                "C0002",
            ],
            "customer_name": [
                "Andi Pratama",
                "Bima Saputra",
            ],
            "segment": [
                "Regular",
                "New",
            ],
            "join_date": [
                "2025-01-01",
                "2025-01-02",
            ],
        }
    )


def test_validate_dataset_name_accepts_supported_dataset() -> None:
    validate_dataset_name("customers")


def test_validate_dataset_name_rejects_unknown_dataset() -> None:
    with pytest.raises(ValueError, match="Unsupported dataset"):
        validate_dataset_name("unknown")


def test_validate_required_columns_passes_for_valid_customers() -> None:
    validate_required_columns(
        customer_dataframe(),
        "customers",
    )


def test_validate_required_columns_detects_missing_column() -> None:
    dataframe = customer_dataframe().drop(
        columns=["join_date"]
    )

    with pytest.raises(
        ValueError,
        match="join_date",
    ):
        validate_required_columns(
            dataframe,
            "customers",
        )


def test_validate_dataframe_rejects_empty_dataset() -> None:
    dataframe = pd.DataFrame(
        columns=[
            "customer_id",
            "customer_name",
            "segment",
            "join_date",
        ]
    )

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        validate_dataframe(
            dataframe,
            "customers",
        )


def test_load_csv_reads_file(tmp_path) -> None:
    csv_path = tmp_path / "customers.csv"

    csv_path.write_text(
        (
            "customer_id,customer_name,segment,join_date\n"
            "C0001,Andi Pratama,Regular,2025-01-01\n"
        ),
        encoding="utf-8",
    )

    dataframe = load_csv(csv_path)

    assert len(dataframe) == 1
    assert dataframe.loc[0, "customer_id"] == "C0001"


def test_load_csv_rejects_missing_file(tmp_path) -> None:
    csv_path = tmp_path / "missing.csv"

    with pytest.raises(
        FileNotFoundError,
        match="CSV file not found",
    ):
        load_csv(csv_path)


def test_validate_ids_passes_for_unique_ids() -> None:
    validate_ids(
        customer_dataframe(),
        "customers",
    )


def test_validate_ids_detects_duplicate_ids() -> None:
    dataframe = customer_dataframe()

    dataframe.loc[1, "customer_id"] = "C0001"

    with pytest.raises(
        ValueError,
        match="duplicate",
    ):
        validate_ids(
            dataframe,
            "customers",
        )


def test_validate_ids_detects_missing_ids() -> None:
    dataframe = customer_dataframe()

    dataframe.loc[1, "customer_id"] = None

    with pytest.raises(
        ValueError,
        match="missing",
    ):
        validate_ids(
            dataframe,
            "customers",
        )


def test_validate_dates_passes_for_valid_dates() -> None:
    validate_dates(
        customer_dataframe(),
        "customers",
    )


def test_validate_dates_detects_invalid_dates() -> None:
    dataframe = customer_dataframe()

    dataframe.loc[1, "join_date"] = "not-a-date"

    with pytest.raises(
        ValueError,
        match="invalid",
    ):
        validate_dates(
            dataframe,
            "customers",
        )


def test_validate_numeric_columns_passes_for_valid_products() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
            "product_name": ["Coffee"],
            "category": ["Coffee"],
            "cost_price": [8000],
            "selling_price": [18000],
        }
    )

    validate_numeric_columns(
        dataframe,
        "products",
    )


def test_validate_numeric_columns_detects_invalid_values() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
            "product_name": ["Coffee"],
            "category": ["Coffee"],
            "cost_price": ["invalid"],
            "selling_price": [18000],
        }
    )

    with pytest.raises(
        ValueError,
        match="invalid numeric",
    ):
        validate_numeric_columns(
            dataframe,
            "products",
        )


def test_validate_import_passes_for_valid_customers() -> None:
    validate_import(
        customer_dataframe(),
        "customers",
    )


def test_normalize_dataframe_preserves_required_columns() -> None:
    normalized = normalize_dataframe(
        customer_dataframe(),
        "customers",
    )

    assert list(normalized.columns) == [
        "customer_id",
        "customer_name",
        "segment",
        "join_date",
    ]


def test_normalize_dataframe_normalizes_dates() -> None:
    dataframe = customer_dataframe()

    dataframe["join_date"] = [
        "2025-01-01 10:30:00",
        "2025-01-02 15:45:00",
    ]

    normalized = normalize_dataframe(
        dataframe,
        "customers",
    )

    assert normalized.loc[0, "join_date"] == "2025-01-01"
    assert normalized.loc[1, "join_date"] == "2025-01-02"


def test_import_dataframe_inserts_rows() -> None:
    connection = create_test_database()

    inserted = import_dataframe(
        connection,
        customer_dataframe(),
        "customers",
    )

    assert inserted == 2

    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    assert count == 2

    connection.close()


def test_import_dataframe_rejects_duplicate_primary_key() -> None:
    connection = create_test_database()

    import_dataframe(
        connection,
        customer_dataframe(),
        "customers",
    )

    duplicate = pd.DataFrame(
        {
            "customer_id": ["C0001"],
            "customer_name": ["Duplicate"],
            "segment": ["Regular"],
            "join_date": ["2025-01-03"],
        }
    )

    with pytest.raises(DatabaseError):
        import_dataframe(
            connection,
            duplicate,
            "customers",
        )

    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    assert count == 2

    connection.close()


def test_import_dataframe_rolls_back_failed_insert() -> None:
    connection = create_test_database()

    dataframe = customer_dataframe()

    dataframe.loc[1, "customer_id"] = "C0001"

    with pytest.raises(
        ValueError,
        match="duplicate",
    ):
        import_dataframe(
            connection,
            dataframe,
            "customers",
        )

    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    assert count == 0

    connection.close()


def test_import_csv_loads_and_inserts_rows(tmp_path) -> None:
    connection = create_test_database()

    csv_path = tmp_path / "customers.csv"

    csv_path.write_text(
        (
            "customer_id,customer_name,segment,join_date\n"
            "C0001,Andi Pratama,Regular,2025-01-01\n"
            "C0002,Bima Saputra,New,2025-01-02\n"
        ),
        encoding="utf-8",
    )

    inserted = import_csv(
        connection,
        csv_path,
        "customers",
    )

    assert inserted == 2

    rows = connection.execute(
        """
        SELECT
            customer_id,
            customer_name,
            segment,
            join_date
        FROM customers
        ORDER BY customer_id
        """
    ).fetchall()

    assert rows == [
        (
            "C0001",
            "Andi Pratama",
            "Regular",
            "2025-01-01",
        ),
        (
            "C0002",
            "Bima Saputra",
            "New",
            "2025-01-02",
        ),
    ]

    connection.close()
