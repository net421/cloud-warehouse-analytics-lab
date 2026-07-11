-- Snowflake-style typed staging and deduplication.
create or replace transient table analytics.stg_order_lines as
select trim(order_line_id) order_line_id, trim(order_id) order_id,
       trim(customer_id) customer_id, try_to_date(order_date) order_date,
       try_to_date(promised_date) promised_date, trim(sku) sku,
       try_to_number(units_ordered) units_ordered,
       try_to_number(units_shipped) units_shipped,
       try_to_decimal(revenue,18,2) revenue, ingestion_timestamp
from raw.erp_order_lines
qualify row_number() over(partition by order_line_id order by ingestion_timestamp desc)=1;
