"""Optional Databricks/Fabric-style Spark Delta sink.

Requires an existing Spark session with Delta capabilities enabled.
"""


def write_delta(rows: list[dict], table: str, mode: str) -> None:
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
    except ImportError as exc:
        raise RuntimeError("PySpark is required for --write-delta; install the spark extra") from exc
    if not table.replace("_", "").replace(".", "").isalnum() or table[0].isdigit():
        raise ValueError("Invalid target table name")
    spark = SparkSession.getActiveSession()
    if spark is None:
        raise RuntimeError("Start a Delta-enabled Spark session before using --write-delta")
    schema = StructType([
        StructField("response_id", IntegerType(), False),
        StructField("source", StringType(), True),
        StructField("page", IntegerType(), True),
        StructField("feedback", StringType(), True),
        StructField("sentiment", StringType(), True),
        StructField("score", DoubleType(), True),
        StructField("themes", StringType(), True),
        StructField("scoring_method", StringType(), True),
    ])
    records = [(i, row["source"], row["page"], row["feedback"], row["sentiment"],
                float(row["score"]), "|".join(row["themes"]), mode) for i, row in enumerate(rows, 1)]
    spark.createDataFrame(records, schema).write.format("delta").mode("append").saveAsTable(table)
