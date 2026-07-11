from pyspark.sql import functions as F

def quality_summary(order_lines):
    return order_lines.agg(
        F.count("*").alias("row_count"),
        F.countDistinct("order_line_id").alias("distinct_order_line_ids"),
        F.sum(F.col("order_line_id").isNull().cast("int")).alias("null_order_line_ids"),
        F.sum((F.col("units_shipped")>F.col("units_ordered")).cast("int")).alias("over_shipped_rows"))
