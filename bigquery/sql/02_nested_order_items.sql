with nested_orders as (
 select order_id,customer_id,order_date,
        array_agg(struct(sku,units_ordered as quantity,revenue as extended_price) order by sku) items
 from `portfolio.analytics.fct_order_lines` group by 1,2,3
)
select order_id,customer_id,order_date,item.sku,item.quantity,item.extended_price
from nested_orders,unnest(items) item;
