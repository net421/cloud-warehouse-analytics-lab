# Grain contracts

| Relation | Grain |
|---|---|
| `clean.fct_order_line` | one row per order line |
| `clean.fct_shipment` | one row per order |
| `analytics.mart_order_fulfillment` | one row per order |
| `analytics.mart_daily_service_level` | one row per order date |
| `analytics.mart_carrier_performance` | one row per carrier |
| `analytics.mart_inventory_risk` | one row per date, warehouse, SKU |
| `analytics.mart_forecast_accuracy` | one row per month, warehouse |

Each grain is validated rather than implied.
