"""PySpark-style transformation examples for a lakehouse lab."""

from pyspark.sql import functions as F


def build_order_metrics(orders_df):
    return (
        orders_df
        .groupBy("customer_id")
        .agg(
            F.countDistinct("order_id").alias("orders_count"),
            F.sum("total_amount").alias("customer_revenue"),
            F.max("order_date").alias("last_order_date")
        )
    )
