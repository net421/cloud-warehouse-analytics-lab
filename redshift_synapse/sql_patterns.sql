-- Redshift/Synapse-style SQL pattern example

select
    date_trunc('month', order_date) as order_month,
    region,
    count(distinct order_id) as orders,
    sum(total_amount) as revenue
from fact_orders
group by 1, 2;
