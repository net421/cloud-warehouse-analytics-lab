# SQL dialect portability

| Concept | DuckDB | Snowflake | BigQuery |
|---|---|---|
| Safe cast | `try_cast` | `TRY_TO_*` | `SAFE_CAST` |
| Nested data | list/struct | `VARIANT` + `FLATTEN` | `ARRAY<STRUCT>` + `UNNEST` |
| Upsert | `MERGE` | `MERGE` | `MERGE` |
| Date difference | `date_diff` | `DATEDIFF` | `DATE_DIFF` |
| Percentiles | `quantile_cont` | percentile functions | percentile / approximate functions |

DuckDB validates business logic locally; platform folders deliberately adapt the dialect.
