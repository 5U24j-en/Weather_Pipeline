import logging
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
LOG4J_CONFIG = ROOT_DIR / "conf" / "log4j2.properties"


def get_spark_session():
    try:
        builder = (
            SparkSession.builder
            .master("local[2]")
            .appName("weather_ETL")
            .config(
                "spark.driver.extraJavaOptions",
                f"-Dlog4j.configurationFile={LOG4J_CONFIG.as_uri()}"
            )
            .config(
                "spark.executor.extraJavaOptions",
                f"-Dlog4j.configurationFile={LOG4J_CONFIG.as_uri()}"
            )
            .config(
                "spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension"
            )
            .config(
               "spark.sql.catalog.spark_catalog",
               "org.apache.spark.sql.delta.catalog.DeltaCatalog"
            )
        )

        spark = configure_spark_with_delta_pip(builder).getOrCreate()

        logger.info("Spark Session created successfully")
        return spark

    except Exception as e:
        logger.critical(
            f"Spark Session creation failed: {e}",
            exc_info=True
        )
        raise