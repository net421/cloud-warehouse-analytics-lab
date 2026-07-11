merge into analytics.fct_order_lines target
using analytics.stg_order_lines source
on target.order_line_id=source.order_line_id
when matched and (target.units_shipped<>source.units_shipped or target.revenue<>source.revenue)
then update set units_shipped=source.units_shipped,revenue=source.revenue,updated_at=current_timestamp()
when not matched then insert(order_line_id,order_id,customer_id,order_date,promised_date,sku,
units_ordered,units_shipped,revenue,updated_at)
values(source.order_line_id,source.order_id,source.customer_id,source.order_date,source.promised_date,
source.sku,source.units_ordered,source.units_shipped,source.revenue,current_timestamp());
