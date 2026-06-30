-- Snowflake-style analytical mart patterns
-- Portfolio lab example, not a production deployment.

with orders as (
    select
        order_id,
        customer_id,
        order_date,
        status,
        total_amount
    from raw_orders
),
customer_order_history as (
    select
        customer_id,
        order_id,
        order_date,
        total_amount,
        row_number() over (partition by customer_id order by order_date) as customer_order_number,
        sum(total_amount) over (partition by customer_id order by order_date rows between unbounded preceding and current row) as customer_lifetime_value
    from orders
)
select *
from customer_order_history;
