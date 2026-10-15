#!/usr/bin/env python3
"""OAF climate-variable contract / Open-Meteo online smoke check.
Runs ONLY as independent CI check; does not fabricate climate data.
"""
import json
import urllib.parse
import urllib.request

LOCATIONS = {"Motupe": (-6.15083, -79.7142), "Chiclayo": (-6.7714, -79.8409)}
C_NOW = ["temperature_2m", "relative_humidity_2m", "precipitation",
         "shortwave_radiation", "wind_speed_10m", "vapour_pressure_deficit",
         "surface_pressure"]
C_DAILY = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
           "precipitation_probability_max", "shortwave_radiation_sum",
           "wind_speed_10m_max", "relative_humidity_2m_mean",
           "vapour_pressure_deficit_max", "et0_fao_evapotranspiration",
           "sunshine_duration"]


def get(url, args):
    full = url + "?" + urllib.parse.urlencode(args)
    req = urllib.request.Request(full, headers={"User-Agent": "OAF-Lambayeque-weather-variables-check/1.0"})
    with urllib.request.urlopen(req, timeout=50) as response:
        result = json.load(response)
    if result.get("error"):
        raise ValueError(result.get("reason", "Error del proveedor"))
    return result


def verify_forecast():
    for place, (lat, lon) in LOCATIONS.items():
        data = get("https://api.open-meteo.com/v1/forecast", {
            "latitude": lat, "longitude": lon, "timezone": "America/Lima",
            "current": ",".join(C_NOW), "daily": ",".join(C_DAILY),
            "forecast_days": 7,
        })
        assert len(data["daily"]["time"]) == 7, place
        for variable in C_NOW:
            value = data["current"].get(variable)
            assert isinstance(value, (float, int)), (place, variable, value)
        for variable in C_DAILY:
            readings = data["daily"].get(variable)
            assert isinstance(readings, list) and len(readings) == 7, (place, variable)
            assert all(v is None or isinstance(v, (int, float)) for v in readings), (place, variable)
        print("Forecast variables present:", place, "radiation units:",
              data.get("daily_units", {}).get("shortwave_radiation_sum"),
              "vpd units:", data.get("daily_units", {}).get("vapour_pressure_deficit_max"))
        assert data["daily_units"].get("shortwave_radiation_sum") in ["MJ/m²", "MJ/m2"], "Unexpected solar radiation units"
        assert data["current_units"].get("shortwave_radiation") in ["W/m²", "W/m2"], "Unexpected current radiation units"
        assert data["daily_units"].get("et0_fao_evapotranspiration") == "mm", "Unexpected ET0 units"


def verify_archive():
    lat, lon = LOCATIONS["Motupe"]
    archive = "https://archive-api.open-meteo.com/v1/archive"
    common = {"latitude": lat, "longitude": lon, "timezone": "America/Lima",
              "start_date": "2019-10-01", "end_date": "2019-10-31"}
    usable = []
    for model in ["era5_land", "era5", "best_match"]:
        try:
            result = get(archive, {**common, "daily": "shortwave_radiation_sum", "models": model})
            values = result["daily"]["shortwave_radiation_sum"]
            count = sum(isinstance(v, (int, float)) for v in values)
            print("HISTORICAL RADIATION:", model, "valid=", count, "unit=", result.get("daily_units",{}).get("shortwave_radiation_sum"), "first=", values[:5])
            if count >= 25:
                usable.append(model)
        except Exception as ex:
            print("HISTORICAL RADIATION:", model, "not available", str(ex)[:160])
    assert "era5" in usable, "Chosen ERA5 historical solar radiation source is missing"
    era5rain = get(archive, {**common, "daily": "precipitation_sum", "models": "era5"})
    assert len(era5rain["daily"]["precipitation_sum"]) == 31
    era5land_temp = get(archive, {**common, "daily": "temperature_2m_mean", "models": "era5_land"})
    assert sum(isinstance(v, (int, float)) for v in era5land_temp["daily"]["temperature_2m_mean"]) >= 25
    print("CHOSEN SOURCES VERIFIED: ERA5 radiation and rain; ERA5-Land temperature")


if __name__ == "__main__":
    verify_forecast()
    verify_archive()
    print("OAF agroclimatic variables: external API smoke checks PASS")
