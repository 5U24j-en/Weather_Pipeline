
from utils.logger import get_logger
from pathlib import Path
import os
from .pincode_csv_data_extract import extract_data, extract_lat_long
from .weather_api_util import weather_api_call
from .api_data_load import save_raw_weather
from utils.spark_session import get_spark_session
from tqdm import tqdm
from pyspark.sql.functions import current_timestamp, current_date
from delta.tables import DeltaTable
import json


logger = get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BRONZE_DELTA_TABLE = ROOT_DIR / "data" / "bronze" / "delta_table"


def run_pipeline(district_name: str = "bengaluru urban"):
    try:
        
        logger.info(f"Pipeline started for {district_name.title()}") # Title converts the Strings first letter to Capital Letter

        df = extract_data()

        cleaned_df = extract_lat_long(df)

        weather_data = weather_api_call(cleaned_df)

        save_raw_weather(weather_data)

        logger.info("Pipeline completed successfully")

        return weather_data
    
    except Exception as e:
        logger.critical(f"Pipeline failed abruptly: {e}", exc_info=True)
        raise


def bronze_pipeline(data):

    spark = get_spark_session()

    bronze_rows = [
        {
            "pincode": item["pincode"],
            "api_call_timestamp": item["api_call_timestamp"],
            "weather_data_time": item["weather_data_time"],
            "response_json": json.dumps(item["response"])
        }
        for item in data
    ]

    bronze_df = spark.createDataFrame(bronze_rows)
    bronze_df = bronze_df.withColumn("bronze_ingestion_date", current_date())
    bronze_df = bronze_df.withColumn("bronze_ingestion_timestamp", current_timestamp())
    (
        bronze_df
            .coalesce(2)
            .write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .partitionBy("bronze_ingestion_date")
            .save(str(BRONZE_DELTA_TABLE))
    )

    logger.info("Bronze Delta table updated successfully")
    return True

if __name__ == "__main__":
    data = run_pipeline(district_name="bengaluru urban")
    try:
        bronze_pipeline(data)
        logger.info("Bronze Pipeline completed successfully")
    except Exception as e:
        logger.exception(f"Weather pipeline execution failed: {e}")
        raise
    