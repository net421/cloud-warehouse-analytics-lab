-- Snowflake VARIANT + FLATTEN.
select event_payload:order_id::string order_id,
       event_payload:event_timestamp::timestamp_ntz event_timestamp,
       item.value:sku::string sku, item.value:quantity::number quantity,
       item.value:extended_price::number(18,2) extended_price
from raw.order_events, lateral flatten(input=>event_payload:items) item
where event_payload:event_type::string='order_created';
