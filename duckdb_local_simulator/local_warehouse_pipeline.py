"""Local DuckDB warehouse simulator.

Creates a simple local analytical mart from CSV-style inputs. This file is a scaffold
for a reproducible local warehouse demo.
"""

import duckdb


def build_local_mart(database_path="warehouse.duckdb"):
    con = duckdb.connect(database_path)
    con.execute("""
        create or replace table fact_orders as
        select
            1 as order_id,
            101 as customer_id,
            date '2026-01-01' as order_date,
            250.00 as total_amount
    """)
    con.execute("""
        create or replace table mart_monthly_revenue as
        select
            date_trunc('month', order_date) as order_month,
            sum(total_amount) as revenue
        from fact_orders
        group by 1
    """)
    return con.execute("select * from mart_monthly_revenue").fetchall()


if __name__ == "__main__":
    print(build_local_mart())
