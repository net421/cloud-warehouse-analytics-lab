create or replace table analytics.mart_order_fulfillment as
with order_rollup as (
    select
        order_id,
        customer_id,
        warehouse,
        min(order_date) as order_date,
        max(promised_date) as promised_date,
        sum(units_ordered) as units_ordered,
        sum(units_shipped) as units_shipped,
        sum(revenue) as recognized_revenue,
        sum(units_shipped * unit_weight_kg) as calculated_shipped_weight_kg,
        count(*) as order_line_count
    from clean.fct_order_line
    group by 1, 2, 3
),
joined as (
    select
        orders.*,
        customers.customer_segment,
        customers.region,
        shipments.shipment_id,
        shipments.carrier,
        shipments.ship_date,
        shipments.delivery_date,
        shipments.shipment_weight_kg,
        shipments.freight_cost,
        shipments.handling_cost,
        shipments.exception_cost
    from order_rollup as orders
    join clean.dim_customer as customers using (customer_id)
    left join clean.fct_shipment as shipments using (order_id)
),
scored as (
    select
        *,
        units_shipped::double / nullif(units_ordered, 0) as unit_fill_rate,
        case when units_shipped >= units_ordered then 1 else 0 end as complete_order_flag,
        case when delivery_date <= promised_date then 1 else 0 end as on_time_flag,
        date_diff('day', order_date, delivery_date) as order_lead_time_days,
        freight_cost / nullif(shipment_weight_kg, 0) as freight_cost_per_kg,
        freight_cost + handling_cost + exception_cost as logistics_cost,
        row_number() over (
            partition by customer_id
            order by order_date, order_id
        ) as customer_order_number,
        sum(recognized_revenue) over (
            partition by customer_id
            order by order_date, order_id
            rows between unbounded preceding and current row
        ) as customer_lifetime_revenue
    from joined
)
select
    *,
    case
        when complete_order_flag = 1 and on_time_flag = 1 then 1
        else 0
    end as otif_flag,
    logistics_cost / nullif(recognized_revenue, 0) as logistics_cost_pct_revenue
from scored;

create or replace table analytics.mart_daily_service_level as
with daily as (
    select
        order_date,
        count(*) as orders,
        sum(units_ordered) as units_ordered,
        sum(units_shipped) as units_shipped,
        avg(complete_order_flag) as complete_order_rate,
        avg(on_time_flag) as on_time_delivery_rate,
        avg(otif_flag) as otif_rate,
        sum(recognized_revenue) as revenue,
        sum(logistics_cost) as logistics_cost
    from analytics.mart_order_fulfillment
    group by 1
),
windowed as (
    select
        *,
        lag(otif_rate) over (order by order_date) as prior_day_otif,
        avg(otif_rate) over (
            order by order_date
            rows between 29 preceding and current row
        ) as rolling_30d_otif,
        sum(revenue) over (
            order by order_date
            rows between 29 preceding and current row
        ) as rolling_30d_revenue
    from daily
)
select
    *,
    units_shipped::double / nullif(units_ordered, 0) as unit_fill_rate,
    otif_rate - prior_day_otif as day_over_day_otif_change
from windowed;

create or replace table analytics.mart_carrier_performance as
with metrics as (
    select
        carrier,
        count(*) as shipments,
        avg(on_time_flag) as on_time_delivery_rate,
        avg(complete_order_flag) as complete_order_rate,
        avg(otif_flag) as otif_rate,
        avg(order_lead_time_days) as average_lead_time_days,
        quantile_cont(order_lead_time_days, 0.5) as median_lead_time_days,
        quantile_cont(order_lead_time_days, 0.9) as p90_lead_time_days,
        sum(freight_cost) as freight_cost,
        sum(shipment_weight_kg) as shipment_weight_kg,
        sum(freight_cost) / nullif(sum(shipment_weight_kg), 0) as freight_cost_per_kg,
        sum(exception_cost) as exception_cost
    from analytics.mart_order_fulfillment
    where carrier is not null
    group by 1
)
select
    *,
    dense_rank() over (
        order by otif_rate desc, freight_cost_per_kg asc
    ) as service_cost_rank,
    percent_rank() over (
        order by p90_lead_time_days
    ) as lead_time_percentile
from metrics;

create or replace table analytics.mart_inventory_risk as
select
    inventory.snapshot_date,
    inventory.warehouse,
    inventory.sku,
    products.product_category,
    products.supplier_id,
    suppliers.supplier_risk_tier,
    inventory.on_hand_units,
    inventory.average_daily_demand,
    inventory.inventory_value,
    inventory.on_hand_units / nullif(inventory.average_daily_demand, 0) as days_of_inventory,
    case
        when inventory.on_hand_units = 0 and inventory.average_daily_demand > 0 then 'STOCKOUT'
        when inventory.on_hand_units / nullif(inventory.average_daily_demand, 0) < 7 then 'CRITICAL'
        when inventory.on_hand_units / nullif(inventory.average_daily_demand, 0) < 14 then 'WATCH'
        when inventory.on_hand_units / nullif(inventory.average_daily_demand, 0) > 90 then 'EXCESS'
        else 'HEALTHY'
    end as inventory_risk_status
from clean.fct_inventory_snapshot as inventory
join clean.dim_product as products using (sku)
join clean.dim_supplier as suppliers using (supplier_id);

create or replace table analytics.mart_forecast_accuracy as
select
    forecast_month,
    warehouse,
    sum(forecast_units) as forecast_units,
    sum(actual_units) as actual_units,
    sum(abs(actual_units - forecast_units))::double / nullif(sum(actual_units), 0) as wape,
    sum(forecast_units - actual_units)::double / nullif(sum(actual_units), 0) as forecast_bias,
    1 - (
        sum(abs(actual_units - forecast_units))::double / nullif(sum(actual_units), 0)
    ) as forecast_accuracy
from clean.fct_demand_forecast
group by 1, 2;
