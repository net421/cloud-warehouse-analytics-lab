"""Local cloud warehouse simulator for the order mart lab.

The script uses DuckDB when it is installed and falls back to SQLite from the
standard library. It keeps the portfolio artifact runnable in lightweight review
environments while still modeling warehouse-style raw, clean, fact, and mart
layers with SQL.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Sequence


LOGGER = logging.getLogger(__name__)


ORDERS = [
    ("O-1001", "C-001", "2025-01-03", "2025-01-04", "2025-01-07", "delivered", "web", "west", 120.00, 10.00, 8.50),
    ("O-1002", "C-002", "2025-01-05", "2025-01-07", "2025-01-10", "delivered", "marketplace", "northeast", 76.40, 0.00, 6.25),
    ("O-1003", "C-001", "2025-01-21", "2025-01-22", "2025-01-24", "returned", "web", "west", 54.20, 5.00, 5.75),
    ("O-1004", "C-003", "2025-02-02", "2025-02-04", "2025-02-08", "delivered", "inside_sales", "south", 310.00, 25.00, 18.00),
    ("O-1005", "C-004", "2025-02-10", None, None, "cancelled", "web", "midwest", 89.99, 0.00, 0.00),
    ("O-1006", "C-002", "2025-02-18", "2025-02-20", "2025-02-24", "delivered", "marketplace", "northeast", 143.50, 15.00, 9.00),
    ("O-1007", "C-005", "2025-03-03", "2025-03-05", None, "shipped", "web", "west", 67.75, 0.00, 7.20),
    ("O-1008", "C-003", "2025-03-14", "2025-03-15", "2025-03-17", "delivered", "inside_sales", "south", 225.00, 0.00, 16.00),
    ("O-1009", "C-006", "2025-03-27", None, None, "placed", "web", "southeast", 44.00, 0.00, 4.50),
    ("O-1010", "C-001", "2025-04-15", "2025-04-16", "2025-04-19", "delivered", "web", "west", 199.00, 20.00, 12.25),
    ("O-1011", "C-004", "2025-04-30", "2025-05-02", "2025-05-06", "delivered", "partner", "midwest", 132.80, 10.00, 8.00),
    ("O-1012", "C-005", "2025-05-20", "2025-05-22", "2025-05-25", "delivered", "web", "west", 91.25, 0.00, 7.50),
]


ORDER_ITEMS = [
    ("O-1001", "SKU-A", "equipment", 2, 35.00),
    ("O-1001", "SKU-B", "accessories", 1, 50.00),
    ("O-1002", "SKU-C", "consumables", 1, 45.00),
    ("O-1002", "SKU-D", "accessories", 2, 15.70),
    ("O-1003", "SKU-E", "accessories", 1, 54.20),
    ("O-1004", "SKU-F", "equipment", 1, 180.00),
    ("O-1004", "SKU-G", "services", 2, 65.00),
    ("O-1005", "SKU-H", "equipment", 1, 89.99),
    ("O-1006", "SKU-I", "equipment", 1, 100.00),
    ("O-1006", "SKU-J", "accessories", 1, 43.50),
    ("O-1007", "SKU-K", "consumables", 1, 67.75),
    ("O-1008", "SKU-L", "services", 3, 75.00),
    ("O-1009", "SKU-M", "consumables", 2, 22.00),
    ("O-1010", "SKU-N", "equipment", 1, 120.00),
    ("O-1010", "SKU-O", "accessories", 1, 79.00),
    ("O-1011", "SKU-P", "equipment", 2, 66.40),
    ("O-1012", "SKU-Q", "services", 1, 91.25),
]


@dataclass(frozen=True)
class ValidationResult:
    name: str
    failing_rows: int


def connect(database_path: str = ":memory:"):
    try:
        import duckdb  # type: ignore

        LOGGER.info("Using DuckDB engine")
        return duckdb.connect(database_path), "duckdb"
    except ModuleNotFoundError:
        LOGGER.info("DuckDB not installed; using SQLite fallback")
        return sqlite3.connect(":memory:" if database_path == ":memory:" else database_path), "sqlite"


def execute_many(con, sql: str, rows: Iterable[Sequence[object]]) -> None:
    con.executemany(sql, list(rows))


def fetch_all(con, sql: str):
    return con.execute(sql).fetchall()


def create_raw_tables(con) -> None:
    con.execute("drop table if exists raw_orders")
    con.execute("drop table if exists raw_order_items")
    con.execute(
        """
        create table raw_orders (
            order_id text,
            customer_id text,
            order_date text,
            shipped_date text,
            delivered_date text,
            status text,
            channel text,
            region text,
            total_amount real,
            discount_amount real,
            freight_amount real
        )
        """
    )
    con.execute(
        """
        create table raw_order_items (
            order_id text,
            sku text,
            product_category text,
            quantity integer,
            unit_price real
        )
        """
    )
    execute_many(con, "insert into raw_orders values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ORDERS)
    execute_many(con, "insert into raw_order_items values (?, ?, ?, ?, ?)", ORDER_ITEMS)


def date_diff_expression(engine: str, start_column: str, end_column: str) -> str:
    if engine == "duckdb":
        return f"date_diff('day', cast({start_column} as date), cast({end_column} as date))"
    return f"cast(julianday({end_column}) - julianday({start_column}) as integer)"


def build_marts(con, engine: str) -> None:
    days_to_ship = date_diff_expression(engine, "orders.order_date", "orders.shipped_date")
    days_to_deliver = date_diff_expression(engine, "orders.order_date", "orders.delivered_date")
    days_since_previous = date_diff_expression(engine, "previous_order_date", "order_date")

    con.execute("drop table if exists clean_orders")
    con.execute("drop table if exists fact_order_items")
    con.execute("drop table if exists mart_customer_order_lifecycle")
    con.execute("drop table if exists mart_channel_region_kpis")

    con.execute(
        """
        create table clean_orders as
        select
            trim(order_id) as order_id,
            trim(customer_id) as customer_id,
            order_date,
            shipped_date,
            delivered_date,
            case
                when lower(trim(status)) in ('placed', 'pending') then 'placed'
                when lower(trim(status)) in ('shipped', 'in_transit') then 'shipped'
                when lower(trim(status)) in ('delivered', 'complete', 'completed') then 'delivered'
                when lower(trim(status)) in ('cancelled', 'canceled') then 'cancelled'
                when lower(trim(status)) in ('returned', 'refunded') then 'returned'
                else 'unknown'
            end as status,
            lower(trim(channel)) as channel,
            lower(trim(region)) as region,
            total_amount,
            coalesce(discount_amount, 0) as discount_amount,
            coalesce(freight_amount, 0) as freight_amount,
            total_amount - coalesce(discount_amount, 0) as net_order_amount
        from raw_orders
        """
    )

    con.execute(
        f"""
        create table fact_order_items as
        with item_lines as (
            select
                order_id,
                sku,
                product_category,
                quantity,
                unit_price,
                quantity * unit_price as line_gross_amount
            from raw_order_items
        ),
        allocated as (
            select
                orders.order_id,
                orders.customer_id,
                orders.order_date,
                orders.shipped_date,
                orders.delivered_date,
                orders.status,
                orders.channel,
                orders.region,
                items.sku,
                items.product_category,
                items.quantity,
                items.unit_price,
                items.line_gross_amount,
                orders.total_amount,
                orders.discount_amount,
                orders.freight_amount,
                orders.net_order_amount,
                sum(items.line_gross_amount) over (partition by orders.order_id) as order_item_gross_amount
            from clean_orders as orders
            inner join item_lines as items
                on orders.order_id = items.order_id
        )
        select
            order_id,
            customer_id,
            order_date,
            shipped_date,
            delivered_date,
            status,
            channel,
            region,
            sku,
            product_category,
            quantity,
            unit_price,
            line_gross_amount,
            round(discount_amount * line_gross_amount / nullif(order_item_gross_amount, 0), 2) as allocated_discount_amount,
            round(line_gross_amount - discount_amount * line_gross_amount / nullif(order_item_gross_amount, 0), 2) as net_line_amount,
            case
                when status in ('shipped', 'delivered')
                    then round(line_gross_amount - discount_amount * line_gross_amount / nullif(order_item_gross_amount, 0), 2)
                else 0
            end as recognized_line_revenue_amount,
            total_amount,
            discount_amount,
            freight_amount,
            net_order_amount,
            {days_to_ship} as days_to_ship,
            {days_to_deliver} as days_to_deliver
        from allocated as orders
        """
    )

    con.execute(
        f"""
        create table mart_customer_order_lifecycle as
        with order_rollup as (
            select
                order_id,
                customer_id,
                order_date,
                status,
                channel,
                region,
                max(shipped_date) as shipped_date,
                max(delivered_date) as delivered_date,
                round(sum(recognized_line_revenue_amount), 2) as recognized_revenue_amount,
                max(net_order_amount) as net_order_amount,
                max(days_to_ship) as days_to_ship,
                max(days_to_deliver) as days_to_deliver
            from fact_order_items
            group by 1, 2, 3, 4, 5, 6
        ),
        customer_windows as (
            select
                *,
                row_number() over (
                    partition by customer_id
                    order by order_date, order_id
                ) as customer_order_number,
                lag(order_date) over (
                    partition by customer_id
                    order by order_date, order_id
                ) as previous_order_date,
                round(
                    sum(recognized_revenue_amount) over (
                        partition by customer_id
                        order by order_date, order_id
                        rows between unbounded preceding and current row
                    ),
                    2
                ) as customer_revenue_to_date
            from order_rollup
        )
        select
            *,
            {days_since_previous} as days_since_previous_order,
            case
                when previous_order_date is null then 'new'
                when {days_since_previous} > 60 then 'reactivated'
                else 'returning'
            end as customer_order_stage
        from customer_windows
        """
    )

    con.execute(
        """
        create table mart_channel_region_kpis as
        select
            substr(order_date, 1, 7) as order_month,
            channel,
            region,
            count(distinct order_id) as orders_count,
            round(sum(recognized_revenue_amount), 2) as recognized_revenue_amount,
            sum(case when status in ('cancelled', 'returned') then 1 else 0 end) as exception_order_count,
            round(avg(days_to_ship), 2) as avg_days_to_ship
        from mart_customer_order_lifecycle
        group by 1, 2, 3
        """
    )


VALIDATION_QUERIES = {
    "unique_order_item_grain": """
        select order_id, sku, count(*) as row_count
        from fact_order_items
        group by 1, 2
        having count(*) > 1
    """,
    "non_negative_financials": """
        select order_id, sku
        from fact_order_items
        where net_line_amount < 0
            or recognized_line_revenue_amount < 0
            or allocated_discount_amount < 0
    """,
    "forward_moving_lifecycle_dates": """
        select order_id, sku
        from fact_order_items
        where (shipped_date is not null and shipped_date < order_date)
            or (delivered_date is not null and shipped_date is not null and delivered_date < shipped_date)
            or days_to_ship < 0
            or days_to_deliver < 0
    """,
    "line_allocation_ties_to_order_net_amount": """
        select
            order_id,
            round(sum(net_line_amount), 2) as line_net_amount,
            max(net_order_amount) as order_net_amount
        from fact_order_items
        group by 1
        having abs(round(sum(net_line_amount), 2) - max(net_order_amount)) > 0.05
    """,
    "customer_sequence_is_gapless": """
        with sequenced as (
            select
                order_id,
                customer_id,
                customer_order_number,
                row_number() over (
                    partition by customer_id
                    order by order_date, order_id
                ) as expected_customer_order_number
            from mart_customer_order_lifecycle
        )
        select *
        from sequenced
        where customer_order_number <> expected_customer_order_number
    """,
}


def validate_marts(con) -> list[ValidationResult]:
    results = []
    for name, query in VALIDATION_QUERIES.items():
        failing_rows = len(fetch_all(con, query))
        results.append(ValidationResult(name=name, failing_rows=failing_rows))
    return results


def summarize_marts(con) -> dict[str, object]:
    total_revenue = fetch_all(
        con,
        "select round(sum(recognized_revenue_amount), 2) from mart_customer_order_lifecycle",
    )[0][0]
    customer_count = fetch_all(con, "select count(distinct customer_id) from mart_customer_order_lifecycle")[0][0]
    exception_orders = fetch_all(
        con,
        "select count(*) from mart_customer_order_lifecycle where status in ('cancelled', 'returned')",
    )[0][0]
    return {
        "recognized_revenue_amount": total_revenue,
        "customers": customer_count,
        "exception_orders": exception_orders,
        "channel_region_rows": len(fetch_all(con, "select * from mart_channel_region_kpis")),
    }


def build_local_mart(database_path: str = ":memory:") -> dict[str, object]:
    con, engine = connect(database_path)
    LOGGER.info("Creating raw tables")
    create_raw_tables(con)
    LOGGER.info("Building clean, fact, and mart tables")
    build_marts(con, engine)
    validation_results = validate_marts(con)
    failing_checks = [result for result in validation_results if result.failing_rows > 0]
    if failing_checks:
        details = ", ".join(f"{result.name}={result.failing_rows}" for result in failing_checks)
        raise AssertionError(f"Warehouse validation failed: {details}")

    summary = summarize_marts(con)
    summary["engine"] = engine
    summary["validation_checks"] = len(validation_results)
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(build_local_mart())
