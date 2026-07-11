create or replace table clean.dim_customer as
select
    trim(customer_id) as customer_id,
    trim(customer_segment) as customer_segment,
    trim(region) as region
from raw.customers;

create or replace table clean.dim_supplier as
select
    trim(supplier_id) as supplier_id,
    trim(supplier_name) as supplier_name,
    cast(base_lead_time_days as integer) as base_lead_time_days,
    trim(supplier_risk_tier) as supplier_risk_tier
from raw.suppliers;

create or replace table clean.dim_product as
select
    trim(sku) as sku,
    trim(product_category) as product_category,
    trim(supplier_id) as supplier_id,
    cast(unit_price as decimal(18, 2)) as unit_price,
    cast(unit_weight_kg as decimal(18, 3)) as unit_weight_kg
from raw.products;

create or replace table clean.fct_order_line as
select
    trim(order_line_id) as order_line_id,
    trim(order_id) as order_id,
    trim(customer_id) as customer_id,
    trim(warehouse) as warehouse,
    cast(order_date as date) as order_date,
    cast(promised_date as date) as promised_date,
    trim(sku) as sku,
    trim(supplier_id) as supplier_id,
    cast(units_ordered as integer) as units_ordered,
    cast(units_shipped as integer) as units_shipped,
    cast(unit_price as decimal(18, 2)) as unit_price,
    cast(unit_weight_kg as decimal(18, 3)) as unit_weight_kg,
    cast(revenue as decimal(18, 2)) as revenue
from raw.erp_order_lines;

create or replace table clean.fct_shipment as
select
    trim(shipment_id) as shipment_id,
    trim(order_id) as order_id,
    trim(carrier) as carrier,
    trim(warehouse) as warehouse,
    cast(ship_date as date) as ship_date,
    cast(delivery_date as date) as delivery_date,
    cast(promised_date as date) as promised_date,
    cast(shipment_weight_kg as decimal(18, 3)) as shipment_weight_kg,
    cast(freight_cost as decimal(18, 2)) as freight_cost,
    cast(handling_cost as decimal(18, 2)) as handling_cost,
    cast(exception_cost as decimal(18, 2)) as exception_cost,
    cast(on_time as boolean) as source_on_time
from raw.tms_shipments;

create or replace table clean.fct_inventory_snapshot as
select
    cast(snapshot_date as date) as snapshot_date,
    trim(warehouse) as warehouse,
    trim(sku) as sku,
    cast(on_hand_units as integer) as on_hand_units,
    cast(average_daily_demand as decimal(18, 3)) as average_daily_demand,
    cast(inventory_value as decimal(18, 2)) as inventory_value
from raw.wms_inventory_snapshots;

create or replace table clean.fct_demand_forecast as
select
    cast("month" as date) as forecast_month,
    trim(warehouse) as warehouse,
    trim(sku) as sku,
    cast(forecast_units as integer) as forecast_units,
    cast(actual_units as integer) as actual_units
from raw.demand_forecasts;
