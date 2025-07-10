
import streamlit as st
import pydeck as pdk
import pandas as pd

# Sidebar navigation
screen = st.sidebar.radio("Choose a screen:", ["Current Weather", "Forecast", "Historical Data"])

# Display content based on selection
if screen == "Current Weather":
    st.title("Current Weather")
    st.write("Welcome to the Current Weather screen.")

    # Example coordinates
    latitude = 42.0308
    longitude = -93.6319

    # Create a DataFrame with the coordinates
    df = pd.DataFrame({
        'lat': [latitude],
        'lon': [longitude]
    })

    # Display the map
    st.map(df)


elif screen == "Forecast":
    st.title("Forecast Screen")
    st.write("Here is the weather forecast.")




    
elif screen == "Historical Data":
    st.title("Historical Data Screen")
    st.write("View historical weather data here.")


