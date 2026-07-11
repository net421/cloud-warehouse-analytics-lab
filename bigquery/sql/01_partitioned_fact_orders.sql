create or replace table `portfolio.analytics.fct_order_lines`
partition by order_date cluster by warehouse,customer_id,sku as
select cast(order_line_id as string) order_line_id,cast(order_id as string) order_id,
       cast(customer_id as string) customer_id,cast(warehouse as string) warehouse,
       safe_cast(order_date as date) order_date,safe_cast(promised_date as date) promised_date,
       cast(sku as string) sku,safe_cast(units_ordered as int64) units_ordered,
       safe_cast(units_shipped as int64) units_shipped,safe_cast(revenue as numeric) revenue
from `portfolio.raw.erp_order_lines`
qualify row_number() over(partition by order_line_id order by ingestion_timestamp desc)=1;
