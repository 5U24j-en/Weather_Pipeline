import logging
from utils.spark_session import get_spark_session
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


ROOT_DIR = Path(__file__).resolve().parent.parent.parent

print(ROOT_DIR)

# Importing and getting a spark session object
spark = get_spark_session()




