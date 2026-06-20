import requests
import os
import time
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="weather_pipeline.log",
    filemode="a"   # append mode
)

logger = logging.getLogger(__name__)

API_KEY = ""

def weather_api_call(df: pd.DataFrame) -> dict:
    weather_api_json = {}
    
    
    for row in df.itertuples(index=False):
    #itertuples is faster than itterows


        try:
            #Payload
            geo_payload = {
                "lat": row.latitude,
                "lon": row.longitude,
                "units": "metric",
                "appid": API_KEY
            }

            # Implementing Logging
            logger.info(f"Calling API for pincode {row.pincode}")

            
            # OpenWeather API Call
            weather_api_response = requests.get(
                "", 
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
            weather_api_json[row.pincode] = {
                "api_call_timestamp": datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
                "weather_data_time": ist_time.isoformat(),
                "response": result
            }

            # Log the API call was success
            logger.info(f"Success for pincode {row.pincode}")
            
            #Rate Limiting
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logger.error(f"API error for pincode {row.pincode}: {e}")

        except ValueError as e:
            logger.error(f"Data issue for pincode {row.pincode}: {e}")

        except Exception as e:
            logger.exception(f"Unexpected error for pincode {row.pincode}")

    return weather_api_json
        
        