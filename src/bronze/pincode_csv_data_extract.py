import pandas as pd
from utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR.joinpath("data")


def extract_data() -> pd.DataFrame:

    csv_file_path = DATA_DIR.joinpath("5c2f62fe-5afa-4119-a499-fec9d604d5bd.csv")
    try:
        logger.info("Starting data extraction")
        df = pd.read_csv(csv_file_path)
        logger.info(f"Data loaded successfully. Rows: {len(df)}, Columns: {len(df.columns)}")
        return df

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during extraction: {e}")
        raise

def extract_lat_long(df: pd.DataFrame, target_district = "bengaluru urban") -> pd.DataFrame:
    
    # From the CSV Filter out the Bengluru Urban Pincode, lat, long

    try:
        logger.info(f"Data Cleaning started for district : {target_district}")

        # Main DF Filtering by - filling NULL values with empty string, removing spaces and lower casing 
        mask = df["district"].fillna("").str.strip().str.lower() == target_district.lower()
        
        # DF should only have pincode , latitude , longitude
        filtered_df = df[mask][["pincode", "latitude", "longitude"]]

        # Droping Duplicate Pincodes
        final_df = filtered_df.drop_duplicates(subset=["pincode"])
       
        # Return Cleaned DF
        logger.info(f"Extraction complete. Found {len(final_df)} unique pincodes.")
        return final_df

        

    except Exception as e:
        logger.exception(f"Unexpected error during Data cleaning : {e}")
        raise