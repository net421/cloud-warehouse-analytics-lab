-- Redshift
create table analytics.fct_order_lines distkey(order_id) sortkey(order_date) as
select * from staging.stg_order_lines;

-- Synapse dedicated SQL pool
create table analytics.fct_order_lines
with(distribution=hash(order_id),clustered columnstore index) as
select * from staging.stg_order_lines;
