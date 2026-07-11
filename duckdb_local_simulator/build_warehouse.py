"""Build the executable local analytical warehouse."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "source"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
SQL_DIR = Path(__file__).resolve().parent / "sql"

SOURCE_FILES = {
    "customers": "customers.csv",
    "suppliers": "suppliers.csv",
    "products": "products.csv",
    "erp_order_lines": "erp_order_lines.csv",
    "tms_shipments": "tms_shipments.csv",
    "wms_inventory_snapshots": "wms_inventory_snapshots.csv",
    "demand_forecasts": "demand_forecasts.csv",
    "warehouse_activity": "warehouse_activity.csv",
}

EXPORTS = {
    "analytics.mart_order_fulfillment": (
        "mart_order_fulfillment.csv",
        "order by customer_id, order_date, order_id",
    ),
    "analytics.mart_daily_service_level": (
        "mart_daily_service_level.csv",
        "order by order_date",
    ),
    "analytics.mart_carrier_performance": (
        "mart_carrier_performance.csv",
        "order by carrier",
    ),
    "analytics.mart_inventory_risk": (
        "mart_inventory_risk.csv",
        "order by snapshot_date, warehouse, sku",
    ),
    "analytics.mart_forecast_accuracy": (
        "mart_forecast_accuracy.csv",
        "order by forecast_month, warehouse",
    ),
    "quality.data_quality_report": (
        "data_quality_report.csv",
        "order by check_name",
    ),
}


def sql_literal(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def load_raw_sources(connection: duckdb.DuckDBPyConnection, data_dir: Path) -> None:
    connection.execute("create schema if not exists raw")
    for table, filename in SOURCE_FILES.items():
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(path)
        connection.execute(
            f"""create or replace table raw.{table} as
                select *
                from read_csv_auto(
                    '{sql_literal(path)}',
                    header=true,
                    sample_size=-1
                )"""
        )


def execute_sql(connection: duckdb.DuckDBPyConnection) -> None:
    for schema in ("clean", "analytics", "quality"):
        connection.execute(f"create schema if not exists {schema}")
    for filename in (
        "01_clean_dimensions.sql",
        "02_date_dimension.sql",
        "03_marts.sql",
        "04_quality.sql",
    ):
        connection.execute((SQL_DIR / filename).read_text(encoding="utf-8"))


def export_marts(connection: duckdb.DuckDBPyConnection, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for relation, (filename, order_by) in EXPORTS.items():
        path = output_dir / filename
        connection.execute(
            f"""copy (
                    select * from {relation} {order_by}
                )
                to '{sql_literal(path)}'
                (header, delimiter ',')"""
        )


def build_warehouse(
    data_dir: Path = DEFAULT_DATA_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    database_path: Path | None = None,
) -> Path:
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path = Path(database_path) if database_path else output_dir / "warehouse.duckdb"
    if database_path.exists():
        database_path.unlink()

    with duckdb.connect(str(database_path)) as connection:
        load_raw_sources(connection, data_dir)
        execute_sql(connection)
        export_marts(connection, output_dir)

        failures = connection.execute(
            "select count(*) from quality.data_quality_report where status <> 'PASS'"
        ).fetchone()[0]
        if failures:
            names = [
                row[0]
                for row in connection.execute(
                    "select check_name from quality.data_quality_report where status <> 'PASS'"
                ).fetchall()
            ]
            raise RuntimeError("Failed checks: " + ", ".join(names))

        summary = connection.execute(
            """select
                   count(*),
                   round(avg(unit_fill_rate) * 100, 2),
                   round(avg(otif_flag) * 100, 2),
                   round(sum(recognized_revenue), 2)
               from analytics.mart_order_fulfillment"""
        ).fetchone()

    print(
        "Warehouse built: "
        f"orders={summary[0]:,}, "
        f"fill={summary[1]}%, "
        f"OTIF={summary[2]}%, "
        f"revenue={summary[3]:,.2f}"
    )
    return database_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--database-path", type=Path)
    arguments = parser.parse_args()
    build_warehouse(arguments.data_dir, arguments.output_dir, arguments.database_path)
