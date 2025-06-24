#!/usr/bin/env python3

import argparse
import requests
import sys
from datetime import datetime
from statistics import mean
from datetime import timedelta

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

def get_month_dates(month_name, year):
    try:
        start_date = datetime.strptime(f"{month_name} 1 {year}", "%B %d %Y")
    except ValueError:
        sys.exit(f"Invalid month name: {month_name}")
    if start_date.month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, start_date.month + 1, 1)
    return start_date.strftime("%Y-%m-%d"), (end_date - timedelta(days=1)).strftime("%Y-%m-%d")

def get_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        sys.exit(f"Error fetching historical data: {start_date} to {end_date}")
    return response.json()["daily"]

def summarize_monthly_data(data):
    days = len(data["time"])
    rainfall = data["precipitation_sum"]
    t_max = data["temperature_2m_max"]
    t_min = data["temperature_2m_min"]

    rainy_days = sum(1 for r in rainfall if r > 0)
    avg_rainfall = round(sum(rainfall) / days, 2)
    min_temp = min(t_min)
    max_temp = max(t_max)

    return {
        "rainy_days": rainy_days,
        "avg_rainfall": avg_rainfall,
        "temp_range": f"{min_temp}°F – {max_temp}°F"
    }

def main():
    # all import need to go to the stat of the file

    parser = argparse.ArgumentParser(description="Get historical weather trends by month and year.")
    parser.add_argument("--location", required=True, help="City name (e.g. 'Seattle')")
    parser.add_argument("--month", required=True, help="Month name (e.g. 'May')")
    parser.add_argument("--years", type=int, default=3, help="Number of years to go back (default 3)")
    args = parser.parse_args()

    lat, lon, city_display = get_coordinates(args.location)

    print(f"\nHistorical Weather in {city_display} for {args.month.title()} (last {args.years} years):\n")

    current_year = datetime.now().year
    for offset in range(args.years):
        year = current_year - offset - 1  # Exclude current year as it may be incomplete
        start, end = get_month_dates(args.month, year)
        data = get_historical_weather(lat, lon, start, end)
        summary = summarize_monthly_data(data)

        print(f"{year}:")
        print(f"  • Average Daily Rainfall: {summary['avg_rainfall']} in")
        print(f"  • Rainy Days: {summary['rainy_days']} days")
        print(f"  • Temperature Range: {summary['temp_range']}\n")

if __name__ == "__main__":
    main()