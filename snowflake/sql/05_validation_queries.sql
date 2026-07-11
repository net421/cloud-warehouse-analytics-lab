select order_line_id,count(*) row_count from analytics.fct_order_lines group by 1 having count(*)>1;
select * from analytics.mart_order_fulfillment
where unit_fill_rate not between 0 and 1
   or otif_flag>on_time_flag or otif_flag>complete_order_flag;
