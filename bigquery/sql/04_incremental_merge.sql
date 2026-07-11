merge `portfolio.analytics.fct_order_lines` target
using `portfolio.staging.stg_order_lines` source
on target.order_line_id=source.order_line_id
when matched then update set units_shipped=source.units_shipped,revenue=source.revenue,
updated_at=current_timestamp()
when not matched then insert row;
