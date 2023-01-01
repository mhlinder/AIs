from datetime import datetime
import joblib
import pandas as pd
import requests
import pytz

flight_key = open("aviation-stack.txt").read().rstrip()

if fetch_flights:

    Kpages = 5 # pagination deep to go

    all_data = []
    for iata in ["BOS", "CAN", "CDG", "DEL", "DXB", "LAX", "SVO"]:
        print(iata, end=" ")
        for k in range(Kpages-2):
            print(k+3, end=" ")
            offset = 100*(k+2)
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

    joblib.dump(flights, "flights.joblib")

else:

    flights = joblib.load("flights.joblib")

departures = pd.DataFrame(flights.departure.values.tolist())
arrivals = pd.DataFrame(flights.arrival.values.tolist())

flights[["departure_airport", "departure_iata"]] = departures[["airport", "iata"]]
flights[["arrival_airport", "arrival_iata"]] = arrivals[["airport", "iata"]]

flights["arrival_actual"] = pd.to_datetime(arrivals.actual_runway)


now = datetime(2023, 1, 1, 16, 58, tzinfo=pytz.utc)
