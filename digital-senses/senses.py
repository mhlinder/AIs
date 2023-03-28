import json
from datetime import datetime

import joblib
import pandas as pd
import pytz
import requests

fetch_flights = False

fetch_tweets = False


def fetch_flight_data(Kpages=5):
    flight_key = open("aviation-stack.txt").read().rstrip()

    all_data = []
    for iata in ["BOS", "DEL", "DXB", "FRA", "SYD"]:
        print(iata, end=" ")
        for k in range(Kpages):
            print(k, end=" ")
            offset = 100 * k
            res = requests.get(
                "".join(
                    [
                        "http://api.aviationstack.com/v1/",
                        "flights?",
                        "&".join(
                            [
                                f"access_key={flight_key}",
                                "limit=100",
                                "flight_status=landed",
                                f"arr_iata={iata}",
                                f"offset={offset}",
                            ]
                        ),
                    ]
                )
            )
            j = res.json()
            try:
                all_data += j["data"]
            except:
                print("fail", end=" ")
        print("Done.")
    flights = pd.DataFrame(all_data)

    return flights


def format_flights(f):
    flights = f.copy()
    departures = pd.DataFrame(flights.departure.values.tolist())
    arrivals = pd.DataFrame(flights.arrival.values.tolist())

    flights[["departure_airport", "departure_iata"]] = departures[["airport", "iata"]]
    flights[["arrival_airport", "arrival_iata"]] = arrivals[["airport", "iata"]]

    flights["arrival_actual"] = pd.to_datetime(arrivals.actual_runway)

    flights["hour"] = flights["arrival_actual"].dt.hour
    flights["day"] = flights["arrival_actual"].dt.day
    flights["year"] = flights["arrival_actual"].dt.year
    flights["month"] = flights["arrival_actual"].dt.month

    flights = flights.dropna(subset="arrival_actual")
    return flights


if fetch_flights:

    inflights = fetch_flight_data()

    joblib.dump(flights, "flights.joblib")

else:

    inflights = joblib.load("flights.joblib")

flights = format_flights(inflights)

flight_counts = (
    flights.groupby(
        [
            "arrival_airport",
            "arrival_iata",
            "departure_airport",
            "departure_iata",
            "year",
            "month",
            "day",
            "hour",
        ]
    )
    .size()
    .sort_values()
)

#

def fetch_tweet_data():
    twitter = json.load(open("twitter.json"))

    headers = {
        "Authorization": f"""Bearer {twitter["bearer_token"]}""",
        "User-Agent": "v2FilteredStreamPython",
    }

    # Operations on filtered stream
    # 
    # fetch current rules
    # res = requests.get("https://api.twitter.com/2/tweets/search/stream/rules", headers=headers)
    # 
    # populate one rule
    # res = requests.post("https://api.twitter.com/2/tweets/search/stream/rules", headers=headers, json={"add": [{"value": "weather lang:en -(new year) (happy OR sad OR angry OR excited OR scared OR disappointed OR surprised OR glad OR good OR bad OR ugly OR beautiful OR fun OR boring OR inside OR outside OR rain OR snow OR sunshine OR warm OR cold)", "tag": "weather sentiment"}]})

    res = requests.get(
        "https://api.twitter.com/2/tweets/search/stream",
        headers=headers,
        stream=True,
    )

    all_out = []
    while len(all_out) < 1000:
        k = 0
        for i, line in enumerate(res.iter_lines()):
            if line:
                if len(all_out) % 10 == 0:
                    print(f"""{datetime.now().strftime("%I:%M:%S")} k={len(all_out)}""")
                    print(f"{line}\n")
                j = json.loads(line)
                all_out.append(j)

    joblib.dump(all_out, "raw-tweets.joblib")

    now = datetime(2023, 1, 1, 16, 58, tzinfo=pytz.utc)
