#!/usr/bin/env python3

import argparse
import requests
import sys

def get_coordinates(city_name):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "en", "format": "json","country":"US" } # CH added US
    response = requests.get(geo_url, params=params)
    if response.status_code != 200:
        sys.exit("Error: Could not fetch geolocation.")
    data = response.json()
    if not data.get("results"):
        sys.exit(f"Location not found: {city_name}")
    loc = data["results"][0]
    return loc["latitude"], loc["longitude"], loc["name"]

def get_weather(latitude, longitude):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,  # Without that we will only return forecast data (hourly, daily, etc.) and not the current weather snapshot.
        "hourly": "temperature_2m,is_day,precipitation,wind_speed_10m,wind_direction_10m,weathercode,uv_index",
        "temperature_unit": "fahrenheit",
        "timezone": "auto"
    }
    response = requests.get(weather_url, params=params)
    if response.status_code != 200:
        sys.exit("Error: Could not fetch weather data.")
    #return response.json()["current"]
    print(response.json()["current_weather"]) # CH added this line to print the current weather
    print(response.json()["hourly"]) # CH added this line to print the hourly weather
    return response.json()["hourly"] 
    # CH changed to hourly b/c current_weather only give you temperature, windspeed, winddirection and weathercode
    # but not precipitation, uv_index, etc. If you want to use current_weather, you need to change format_weather 
    # to only use temperature, windspeed, winddirection and weathercode. 
    # https://open-meteo.com/en/docs#weather_variable_documentation

def degrees_to_cardinal(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees + 22.5) // 45) % 8
    return directions[idx]

def main():
    #parser = argparse.ArgumentParser(description="Check the current weather for a city.")
    #parser.add_argument("--location", required=True, help="City name (e.g. 'Chicago')")
    #args = parser.parse_args()
    location = "Ames"
    lat, lon, city_display = get_coordinates(location)
    current_weather = get_weather(lat, lon)
    summary = format_weather(city_display, current_weather)
    print(summary)

def format_weather(city, current):
    temp = current["temperature_2m"][0] # get the first temp 
    wind_speed = current["wind_speed_10m"][0]
    wind_dir = current["wind_direction_10m"][0]
    uv = current["uv_index"][0]
    rain = current["precipitation"][0]
    local_time = current["time"][0]
    if rain > 0:
        rain_desc = "light rain"
        suggestion = "Carry an umbrella just in case."
    else:
        rain_desc = "clear skies"
        suggestion = "No umbrella needed."

    wind_dir_str = degrees_to_cardinal(wind_dir)

    return (
        f"Today in {city} at {local_time}: {temp}°F, {rain_desc}, winds {wind_speed} mph {wind_dir_str}. "
        f"UV index: {uv}. {suggestion}"
    )

if __name__ == "__main__":
    main()