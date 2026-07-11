create or replace table clean.dim_date as
with recursive date_spine(calendar_date) as (
    select min(order_date)
    from clean.fct_order_line

    union all

    select calendar_date + interval 1 day
    from date_spine
    where calendar_date < (
        select max(delivery_date)
        from clean.fct_shipment
    )
)
select
    calendar_date,
    extract(year from calendar_date)::integer as calendar_year,
    extract(quarter from calendar_date)::integer as calendar_quarter,
    extract(month from calendar_date)::integer as calendar_month,
    strftime(calendar_date, '%Y-%m') as year_month,
    extract(week from calendar_date)::integer as calendar_week,
    dayname(calendar_date) as day_name,
    case
        when dayofweek(calendar_date) in (0, 6) then true
        else false
    end as is_weekend
from date_spine;
