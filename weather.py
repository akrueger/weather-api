import os
import time
from dotenv import load_dotenv
import requests
from ISStreamer.Streamer import Streamer

load_dotenv()

LOCATION = os.getenv("LOCATION")
API_KEY = os.getenv("API_KEY")
BUCKET_NAME = os.getenv("INITIAL_STATE_BUCKET_NAME")
BUCKET_KEY = os.getenv("INITIAL_STATE_BUCKET_KEY")
ACCESS_KEY = os.getenv("INITIAL_STATE_ACCESS_KEY")
MINUTES_BETWEEN_READS = float(os.getenv("MINUTES_BETWEEN_READS", 5))
BASE_URL = "https://api.tomorrow.io/v4/timelines"
PARAM_MAP = {
    "location": LOCATION,
    "fields": ["temperature", "humidity"],
    "timesteps": "current",
    "units": "imperial",
    "apikey": API_KEY,
}

streamer = Streamer(
    bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY
)


def parseValues(data):
    return data["data"]["timelines"][0]["intervals"][0]["values"]


def logToInitialState(temperature, humidity):
    streamer.log("AUSTIN temperature(F)", temperature)
    streamer.log("AUSTIN humdity(%)", humidity)
    streamer.flush()


def fetchWeatherData():
    response = requests.get(BASE_URL, params=PARAM_MAP)

    if response.status_code == 200:
        values = parseValues(response.json())
        temperature = values["temperature"]
        humidity = values["humidity"]

        logToInitialState(temperature, humidity)


while True:
    try:
        fetchWeatherData()

    except RuntimeError:
        print("RuntimeError, trying again...")
        continue

    time.sleep(60 * MINUTES_BETWEEN_READS)
