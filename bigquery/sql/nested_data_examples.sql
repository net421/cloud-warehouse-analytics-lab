-- BigQuery-style nested data example

select
  order_id,
  customer_id,
  item.sku,
  item.quantity,
  item.extended_price
from `project.dataset.orders`,
unnest(items) as item;
