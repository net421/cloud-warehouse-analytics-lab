-- BigQuery-ready analytical mart pattern.
-- Portfolio lab example, not a production deployment.
-- Assumes source-aligned tables `project.raw.orders` and `project.raw.order_items`.

create or replace table `project.analytics.fact_order_items`
partition by order_date
cluster by customer_id, region, product_category as
with source_orders as (
  select
    nullif(trim(order_id), '') as order_id,
    nullif(trim(customer_id), '') as customer_id,
    safe_cast(order_date as date) as order_date,
    safe_cast(shipped_at as date) as shipped_date,
    safe_cast(delivered_at as date) as delivered_date,
    lower(nullif(trim(status), '')) as status_raw,
    lower(nullif(trim(channel), '')) as channel,
    lower(nullif(trim(region), '')) as region,
    safe_cast(total_amount as numeric) as total_amount,
    coalesce(safe_cast(discount_amount as numeric), 0) as discount_amount,
    coalesce(safe_cast(freight_amount as numeric), 0) as freight_amount
  from `project.raw.orders`
),

clean_orders as (
  select
    order_id,
    customer_id,
    order_date,
    shipped_date,
    delivered_date,
    case
      when status_raw in ('placed', 'pending') then 'placed'
      when status_raw in ('shipped', 'in_transit') then 'shipped'
      when status_raw in ('delivered', 'complete', 'completed') then 'delivered'
      when status_raw in ('cancelled', 'canceled') then 'cancelled'
      when status_raw in ('returned', 'refunded') then 'returned'
      else 'unknown'
    end as status,
    channel,
    region,
    total_amount,
    discount_amount,
    freight_amount,
    total_amount - discount_amount as net_order_amount
  from source_orders
),

item_lines as (
  select
    order_id,
    sku,
    product_category,
    quantity,
    safe_cast(unit_price as numeric) as unit_price,
    quantity * safe_cast(unit_price as numeric) as line_gross_amount
  from `project.raw.order_items`
),

allocated as (
  select
    orders.order_id,
    orders.customer_id,
    orders.order_date,
    orders.shipped_date,
    orders.delivered_date,
    orders.status,
    orders.channel,
    orders.region,
    items.sku,
    items.product_category,
    items.quantity,
    items.unit_price,
    items.line_gross_amount,
    orders.total_amount,
    orders.discount_amount,
    orders.freight_amount,
    orders.net_order_amount,
    sum(items.line_gross_amount) over (partition by orders.order_id) as order_item_gross_amount
  from clean_orders as orders
  inner join item_lines as items
    on orders.order_id = items.order_id
)

select
  order_id,
  customer_id,
  order_date,
  shipped_date,
  delivered_date,
  status,
  channel,
  region,
  sku,
  product_category,
  quantity,
  unit_price,
  line_gross_amount,
  round(discount_amount * safe_divide(line_gross_amount, order_item_gross_amount), 2) as allocated_discount_amount,
  round(line_gross_amount - discount_amount * safe_divide(line_gross_amount, order_item_gross_amount), 2) as net_line_amount,
  case
    when status in ('shipped', 'delivered')
      then round(line_gross_amount - discount_amount * safe_divide(line_gross_amount, order_item_gross_amount), 2)
    else 0
  end as recognized_line_revenue_amount,
  total_amount,
  discount_amount,
  freight_amount,
  net_order_amount,
  date_diff(shipped_date, order_date, day) as days_to_ship,
  date_diff(delivered_date, order_date, day) as days_to_deliver,
  current_timestamp() as modeled_at
from allocated;

create or replace table `project.analytics.mart_customer_order_lifecycle`
partition by order_date
cluster by customer_id, customer_order_stage as
with order_rollup as (
  select
    order_id,
    customer_id,
    order_date,
    status,
    channel,
    region,
    max(shipped_date) as shipped_date,
    max(delivered_date) as delivered_date,
    sum(recognized_line_revenue_amount) as recognized_revenue_amount,
    max(net_order_amount) as net_order_amount,
    max(days_to_ship) as days_to_ship,
    max(days_to_deliver) as days_to_deliver
  from `project.analytics.fact_order_items`
  group by 1, 2, 3, 4, 5, 6
),

customer_windows as (
  select
    *,
    row_number() over (
      partition by customer_id
      order by order_date, order_id
    ) as customer_order_number,
    lag(order_date) over (
      partition by customer_id
      order by order_date, order_id
    ) as previous_order_date,
    sum(recognized_revenue_amount) over (
      partition by customer_id
      order by order_date, order_id
      rows between unbounded preceding and current row
    ) as customer_revenue_to_date
  from order_rollup
)

select
  *,
  date_diff(order_date, previous_order_date, day) as days_since_previous_order,
  case
    when previous_order_date is null then 'new'
    when date_diff(order_date, previous_order_date, day) > 60 then 'reactivated'
    else 'returning'
  end as customer_order_stage
from customer_windows;

-- Validation queries should return zero rows before a BI tool consumes the mart.

select order_id, sku, count(*) as row_count
from `project.analytics.fact_order_items`
group by 1, 2
having count(*) > 1;

select *
from `project.analytics.fact_order_items`
where net_line_amount < 0
  or recognized_line_revenue_amount < 0
  or allocated_discount_amount < 0;

select *
from `project.analytics.fact_order_items`
where (shipped_date is not null and shipped_date < order_date)
  or (delivered_date is not null and shipped_date is not null and delivered_date < shipped_date)
  or days_to_ship < 0
  or days_to_deliver < 0;

select
  order_id,
  round(sum(net_line_amount), 2) as line_net_amount,
  max(net_order_amount) as order_net_amount
from `project.analytics.fact_order_items`
group by 1
having abs(round(sum(net_line_amount), 2) - max(net_order_amount)) > 0.05;
