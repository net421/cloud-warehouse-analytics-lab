from pyspark.sql import functions as F

def build_order_service_gold(order_lines,shipments):
    orders=(order_lines.groupBy("order_id","customer_id","warehouse")
            .agg(F.min("order_date").alias("order_date"),
                 F.max("promised_date").alias("promised_date"),
                 F.sum("units_ordered").alias("units_ordered"),
                 F.sum("units_shipped").alias("units_shipped"),
                 F.sum("revenue").alias("revenue")))
    return (orders.join(shipments,"order_id","left")
            .withColumn("unit_fill_rate",F.col("units_shipped")/F.col("units_ordered"))
            .withColumn("complete_order_flag",(F.col("units_shipped")>=F.col("units_ordered")).cast("int"))
            .withColumn("on_time_flag",(F.col("delivery_date")<=F.col("promised_date")).cast("int"))
            .withColumn("otif_flag",((F.col("units_shipped")>=F.col("units_ordered")) &
                                     (F.col("delivery_date")<=F.col("promised_date"))).cast("int")))
