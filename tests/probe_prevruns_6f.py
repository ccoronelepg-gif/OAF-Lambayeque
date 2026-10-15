#!/usr/bin/env python3
"""Phase 6F feasibility smoke test: archived forecasts issued 24h earlier."""
import json
from urllib.parse import urlencode
from urllib.request import urlopen, Request

def fetch(endpoint, params):
    url=endpoint+"?"+urlencode(params)
    with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-scientific-validation/1.0"}), timeout=70) as response:
        data=json.load(response)
    if data.get("error"):
        raise ValueError(data.get("reason"))
    return data

params={"latitude":-6.15083, "longitude":-79.7142,"timezone":"America/Lima",
        "start_date":"2025-07-01","end_date":"2025-07-05"}
fore_vars=["temperature_2m_previous_day1","relative_humidity_2m_previous_day1",
           "shortwave_radiation_previous_day1","wind_speed_10m_previous_day1"]
forecast=fetch("https://previous-runs-api.open-meteo.com/v1/forecast",{**params,"hourly":",".join(fore_vars)})
print("Prev run variables:", sorted(forecast.get("hourly",{})))
for k in fore_vars:
    vals=forecast.get("hourly",{}).get(k,[])
    actual=sum(isinstance(x,(int,float)) for x in vals)
    print(k, "coverage", actual, "/",len(vals),"unit",forecast.get("hourly_units",{}).get(k))
    assert actual>=72, "Insufficient historic forecast coverage: "+k
historical=fetch("https://archive-api.open-meteo.com/v1/archive",{**params,"hourly":"temperature_2m","models":"era5_land"})
d=historical["hourly"]
matched=len(set(forecast["hourly"]["time"]) & set(d["time"]))
print("Reanalysis observations:",len(d["time"]),"hours matched",matched)
assert matched>=100
print("PREVIOUS RUNS SMOKE TEST PASSED")
