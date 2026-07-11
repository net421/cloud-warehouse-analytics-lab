select order_line_id,count(*) row_count
from `portfolio.analytics.fct_order_lines` group by 1 having count(*)>1;
select countif(unit_fill_rate not between 0 and 1) invalid_fill_rates,
       countif(otif_flag>on_time_flag) invalid_otif_on_time,
       countif(otif_flag>complete_order_flag) invalid_otif_complete
from `portfolio.analytics.mart_order_fulfillment`;
