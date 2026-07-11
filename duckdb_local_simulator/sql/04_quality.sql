create or replace table quality.data_quality_report as
select 'order_line_key_unique' check_name, count(*) actual_value, count(distinct order_line_id) expected_value,
       case when count(*)=count(distinct order_line_id) then 'PASS' else 'FAIL' end status
from clean.fct_order_line
union all
select 'shipment_order_unique', count(*), count(distinct order_id),
       case when count(*)=count(distinct order_id) then 'PASS' else 'FAIL' end
from clean.fct_shipment
union all
select 'source_to_fact_order_line_count',
       (select count(*) from raw.erp_order_lines),
       (select count(*) from clean.fct_order_line),
       case when (select count(*) from raw.erp_order_lines)=(select count(*) from clean.fct_order_line)
            then 'PASS' else 'FAIL' end
union all
select 'source_to_fact_revenue_reconciliation',
       round((select sum(revenue) from raw.erp_order_lines),2),
       round((select sum(revenue) from clean.fct_order_line),2),
       case when abs((select sum(revenue) from raw.erp_order_lines)-
                     (select sum(revenue) from clean.fct_order_line))<0.01
            then 'PASS' else 'FAIL' end
union all
select 'mart_order_grain_unique', count(*), count(distinct order_id),
       case when count(*)=count(distinct order_id) then 'PASS' else 'FAIL' end
from analytics.mart_order_fulfillment
union all
select 'unit_fill_rate_range',
       count(*) filter(where unit_fill_rate between 0 and 1), count(*),
       case when count(*) filter(where unit_fill_rate between 0 and 1)=count(*)
            then 'PASS' else 'FAIL' end
from analytics.mart_order_fulfillment
union all
select 'otif_not_above_components',
       count(*) filter(where otif_flag<=on_time_flag and otif_flag<=complete_order_flag), count(*),
       case when count(*) filter(where otif_flag<=on_time_flag and otif_flag<=complete_order_flag)=count(*)
            then 'PASS' else 'FAIL' end
from analytics.mart_order_fulfillment
union all
select 'carrier_mart_non_empty', count(*), 1,
       case when count(*)>=1 then 'PASS' else 'FAIL' end
from analytics.mart_carrier_performance
union all
select 'forecast_accuracy_reasonable',
       count(*) filter(where forecast_accuracy between -1 and 1), count(*),
       case when count(*) filter(where forecast_accuracy between -1 and 1)=count(*)
            then 'PASS' else 'FAIL' end
from analytics.mart_forecast_accuracy;
