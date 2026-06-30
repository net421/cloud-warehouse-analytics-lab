# BigQuery Partitioning and Clustering Notes

## Partitioning

Use partitioning for large fact tables where filters commonly use dates such as `order_date`, `event_date`, or `shipment_date`.

## Clustering

Use clustering for frequently filtered or grouped dimensions such as `customer_id`, `region`, `product_category`, or `carrier_id`.

## Portfolio Evidence

This document demonstrates awareness of cost/performance considerations in cloud analytics warehouses.
