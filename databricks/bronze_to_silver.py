from pyspark.sql import functions as F
from pyspark.sql.window import Window

def build_silver_order_lines(bronze):
    latest=Window.partitionBy("order_line_id").orderBy(F.col("ingestion_timestamp").desc())
    return (bronze.withColumn("_rn",F.row_number().over(latest)).filter(F.col("_rn")==1).drop("_rn")
            .withColumn("order_date",F.to_date("order_date"))
            .withColumn("promised_date",F.to_date("promised_date"))
            .withColumn("units_ordered",F.col("units_ordered").cast("int"))
            .withColumn("units_shipped",F.col("units_shipped").cast("int"))
            .withColumn("revenue",F.col("revenue").cast("decimal(18,2)"))
            .filter(F.col("order_line_id").isNotNull()))
