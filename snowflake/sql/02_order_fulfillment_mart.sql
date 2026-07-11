-- Snowflake-style mart with rolling service logic.
create or replace table analytics.mart_order_fulfillment cluster by(order_date,warehouse) as
with orders as (
 select order_id,customer_id,warehouse,min(order_date) order_date,max(promised_date) promised_date,
        sum(units_ordered) units_ordered,sum(units_shipped) units_shipped,sum(revenue) revenue
 from analytics.stg_order_lines group by 1,2,3
), scored as (
 select o.*,s.carrier,s.delivery_date,s.freight_cost,s.shipment_weight_kg,
        units_shipped/nullif(units_ordered,0) unit_fill_rate,
        iff(units_shipped>=units_ordered,1,0) complete_order_flag,
        iff(s.delivery_date<=promised_date,1,0) on_time_flag
 from orders o left join analytics.stg_shipments s using(order_id)
)
select *, iff(complete_order_flag=1 and on_time_flag=1,1,0) otif_flag,
       avg(iff(complete_order_flag=1 and on_time_flag=1,1,0))
       over(order by order_date rows between 29 preceding and current row) rolling_30_order_otif,
       freight_cost/nullif(shipment_weight_kg,0) freight_cost_per_kg
from scored;
