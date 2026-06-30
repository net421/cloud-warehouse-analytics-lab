# Cloud Warehouse Analytics Lab

A simulated, tool-agnostic cloud warehouse analytics lab covering Snowflake-style SQL, BigQuery-ready patterns, Databricks lakehouse concepts, Redshift/Synapse comparisons, and a local DuckDB simulator.

This is a portfolio lab. It demonstrates cloud warehouse concepts and SQL patterns without claiming production enterprise deployment experience.

## Skills Demonstrated

- Cloud warehouse modeling patterns
- Advanced analytical SQL
- Partitioning, clustering and performance notes
- Lakehouse and Delta concepts
- Local warehouse simulation with DuckDB
- Validation-first analytics documentation

## Featured Artifact: Order Mart With Validation

| File | What it proves |
| --- | --- |
| `snowflake/sql/analytics_mart_patterns.sql` | Snowflake-style mart build with CTEs, allocation logic, window functions, clustering intent, and validation queries. |
| `bigquery/sql/order_mart_pattern.sql` | BigQuery-ready equivalent using partitioning, clustering, `SAFE_*` functions, and date logic. |
| `duckdb_local_simulator/local_warehouse_pipeline.py` | Reproducible local simulator that builds raw, clean, fact, and mart tables, then runs data quality checks. |
| `docs/order_mart_validation.md` | KPI dictionary, lineage, warehouse portability notes, and reviewer validation criteria. |

The same business problem appears across the SQL and local simulator: model order-line revenue, allocate discounts, preserve order-item grain, classify customer lifecycle stage, and validate that the mart is safe for BI consumption.

## Local Validation

The simulator uses DuckDB when installed and falls back to standard-library SQLite when DuckDB is unavailable:

```bash
python duckdb_local_simulator/local_warehouse_pipeline.py
```

Expected result:

- source tables are created from synthetic lab data
- warehouse-style marts are built with SQL
- validation checks return zero failing rows
- a small KPI summary is printed for review

## Important Framing

This repository contains lab examples, simulations, and reviewable patterns. It does not claim production ownership of Snowflake, BigQuery, Databricks, Redshift, Synapse, or DuckDB deployments.
