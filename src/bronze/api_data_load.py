import json
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.logger import get_logger
import os
from pathlib import Path

logger = get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
WEATHER_DATA_DIR = ROOT_DIR / "data" / "bronze" / "weather"

def save_raw_weather(data: dict):
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d_%H-%M")

    file_path = WEATHER_DATA_DIR / f"weather_{timestamp}.json"

    WEATHER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"Saved raw weather data to {file_path}")