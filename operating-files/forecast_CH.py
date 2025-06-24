#!/usr/bin/env python3

import argparse
import requests
import sys
import pip
from datetime import datetime
from tabulate import tabulate  # from pip ??? WTH????

# CH: don't duplicate this function, put it into a file called coordinates.py and import it
# here and in weather.py
def get_coordinates(city_name):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    response = requests.get(geo_url, params=params)
    if response.status_code != 200:
        sys.exit("Error: Could not fetch geolocation.")
    data = response.json()
    if not data.get("results"):
        sys.exit(f"Location not found: {city_name}")
    loc = data["results"][0]
    return loc["latitude"], loc["longitude"], loc["name"]

def get_forecast(lat, lon, days, units):
    weather_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": days
    }

    # Unit settings
    if units == "imperial":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
    else:
        params["temperature_unit"] = "celsius"
        params["wind_speed_unit"] = "kmh"

    response = requests.get(weather_url, params=params)
    if response.status_code != 200:
        sys.exit("Error: Could not fetch forecast data.")
    return response.json()

def format_forecast(city, forecast, units):
    daily = forecast["daily"]
    rows = []
    for i in range(len(daily["time"])):
        date = datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%a %b %d")
        t_max = daily["temperature_2m_max"][i]
        t_min = daily["temperature_2m_min"][i]
        rain = daily["precipitation_probability_max"][i]
        wind = daily["wind_speed_10m_max"][i]
        rows.append([date, f"{t_min}° / {t_max}°", f"{rain}%", f"{wind} { 'mph' if units == 'imperial' else 'km/h' }"])

    print(f"\n7-Day Forecast for {city}:\n")
    print(tabulate(rows, headers=["Date", "Temp (Low/High)", "Precip (%)", "Wind"], tablefmt="pretty"))

def main():
    parser = argparse.ArgumentParser(description="Get a 7-day weather forecast.")
    parser.add_argument("--location", required=True, help="City name (e.g. 'Denver')")
    parser.add_argument("--days", type=int, default=7, choices=range(1, 16),
                        help="Number of days (1–15)")
    parser.add_argument("--units", choices=["imperial", "metric"], default="imperial",
                        help="Units: imperial (F, mph) or metric (C, km/h)")

    args = parser.parse_args()

    lat, lon, city_display = get_coordinates(args.location)
    forecast_data = get_forecast(lat, lon, args.days, args.units)
    format_forecast(city_display, forecast_data, args.units)

if __name__ == "__main__":
    main()