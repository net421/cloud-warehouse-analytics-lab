# Snowflake warehouse design

Use separate compute for ingestion, transformation, BI, and ad hoc development. Keep immutable source-aligned data in `RAW`, curated facts/marts in `ANALYTICS`, and exceptions in `QUALITY`. Start with the smallest auto-suspending warehouse and optimize only after inspecting query profiles and pruning.
