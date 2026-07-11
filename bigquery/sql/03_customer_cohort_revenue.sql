with customer_months as (
 select customer_id,date_trunc(order_date,month) activity_month,sum(revenue) revenue
 from `portfolio.analytics.fct_order_lines` group by 1,2
), cohorts as (
 select *,min(activity_month) over(partition by customer_id) cohort_month from customer_months
)
select cohort_month,date_diff(activity_month,cohort_month,month) months_since_first_order,
       count(distinct customer_id) active_customers,sum(revenue) cohort_revenue
from cohorts group by 1,2 order by 1,2;
