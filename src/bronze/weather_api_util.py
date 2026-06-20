import requests
import os
import time
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.logger import get_logger
from tqdm import tqdm
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

API_KEY =  os.getenv("OPENWEATHER_API_KEY")
API_ENDPOINT = os.getenv("OPENWEATHER_API_ENDPOINT")


def api_call(pincode, latitude, longitude):
    with requests.Session() as session:
        try:
            #Payload
            geo_payload = {
                "lat": latitude,
                "lon": longitude,
                "units": "metric",
                "appid": API_KEY
            }
            # OpenWeather API Call
            weather_api_response = session.get(
                API_ENDPOINT, 
                params = geo_payload,
                timeout=5
            ) 
            weather_api_response.raise_for_status()

            # Result will have the API response in dictionary Form
            result=weather_api_response.json()

            # Extract the time of the weather details from the API call
            timestamp = result.get("dt")
            if not timestamp:
                raise ValueError("Missing 'dt' in response")
            
            # Convert it into IST
            ist_time = datetime.fromtimestamp(timestamp, ZoneInfo("Asia/Kolkata"))

            #Updatating Main JSON
            temp = {
                "pincode": pincode,
                "api_call_timestamp": datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
                "weather_data_time": ist_time.isoformat(),
                "response": result
            }

            # Log the API call was success
            logger.info(f"Success for pincode {pincode}")
            #Rate Limiting
            time.sleep(1)
            return(temp)

        except requests.exceptions.RequestException as e:
                logger.error(f"API error for pincode {pincode}: {e}")

        except Exception as e:
            logger.exception(f"Unexpected error for pincode {pincode}")


def weather_api_call(df: pd.DataFrame) -> list[dict]:

    weather_api_json = []
    print("Fetching weather data from API...")
    logger.info("Weather API extraction started")

    with concurrent.futures.ThreadPoolExecutor(10) as executor:

        results = executor.map(
                    api_call,
                    df["pincode"],
                    df["latitude"],
                    df["longitude"]
                )
        
        try:
            weather_api_json = [
                result
                for result in tqdm(
                    results,
                    total=len(df),
                    desc="Fetching Weather Data"
                )
                if result is not None]
        
        except Exception as e:
            logger.exception(f"Worker thread failed: {e}")

    return weather_api_json






