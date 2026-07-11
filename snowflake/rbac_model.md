# Snowflake RBAC model

- `ROLE_INGESTION_RW`: writes only to `RAW`.
- `ROLE_TRANSFORM_RW`: reads `RAW`, writes `ANALYTICS`.
- `ROLE_BI_READ`: reads certified marts only.
- `ROLE_DATA_QUALITY_READ`: reads marts and exceptions.

Service accounts and human analyst roles remain separate.
