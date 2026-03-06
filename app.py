import pandas as pd
import numpy as np
import streamlit as st
from numpy.random import default_rng as rng
import folium
from streamlit_folium import st_folium
import datetime
import requests
import socket


TIMEZONE=""

st.set_page_config(
    page_title="TaxiFare ultimate application!!",
    page_icon="🐍",
    layout="centered", # wide
    initial_sidebar_state="auto") # collapsed

st.sidebar.markdown(f"""
    # Travel information
    """)


#min_lat, max_lat = 40.5, 40.9
#min_lon, max_lon = -74.3, -73.7
#BOUNDING_BOX = (-74.3, -73.7, 40.5, 40.9)

# Initialize session state
if 'pickup_point' not in st.session_state:
    st.session_state.pickup_point = None

if 'dropoff_point' not in st.session_state:
    st.session_state.dropoff_point = None



pickup_date = st.sidebar.date_input(
    "Pickup date",
    datetime.datetime.now())

pickup_time = st.sidebar.time_input('Pickup hour', datetime.datetime.now())
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time)

passenger_count = st.sidebar.number_input('Number of passengers', min_value=1, max_value=8, step=1)

if st.sidebar.button("Clear All Points"):
    st.session_state.pickup_point = None
    st.session_state.dropoff_point = None
    st.rerun()

# Create base map
m = folium.Map(location=[40.5, -74.3], zoom_start=2, max_zoom=18, min_zoom=2)
m.fit_bounds([[40.5, -74.3], [40.9, -73.7]], max_zoom=18)

#display points
if st.session_state.pickup_point is not None: 
    point =  st.session_state.pickup_point
    folium.Marker(
        [point['lat'], point['lon']],
        popup=f"Pickup Point",
        icon=folium.Icon(color='red', icon='cab')
    ).add_to(m)
else:
    st.sidebar.write('Please select a pickup point in the map')



if st.session_state.dropoff_point is not None: 
    point =  st.session_state.dropoff_point
    folium.Marker(
        [point['lat'], point['lon']],
        popup=f"Dropoff Point",
        icon=folium.Icon(color='green', icon='blind')
    ).add_to(m)
else:
    st.sidebar.write('Please select a dropoff point in the map')


# Display map and capture clicks
map_data = st_folium(m, width=700, height=500)

# Process clicks
# if the user has not select a initial and final point

#set pickup point
if map_data and map_data['last_clicked']:
    if st.session_state.pickup_point is None:    
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
    
        # Add to session state
        st.session_state.pickup_point = {
            'lat': clicked_lat,
            'lon': clicked_lon
        }
        
        st.success(f"Point selected: ({clicked_lat:.6f}, {clicked_lon:.6f})")
        st.rerun()

    if st.session_state.dropoff_point is None:    
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
    
        # Add to session state
        st.session_state.dropoff_point = {
            'lat': clicked_lat,
            'lon': clicked_lon
        }
        
        st.success(f"Point selected: ({clicked_lat:.6f}, {clicked_lon:.6f})")
        st.rerun()
    


url = 'https://taxiapi-624873465440.europe-west1.run.app/predict'

if st.sidebar.button('Get fare'):
    # print is visible in the server output, not in the page
    if st.session_state.pickup_point is not None and st.session_state.dropoff_point is not None:
        params = {
            "pickup_datetime": pickup_datetime,  # 2014-07-06 19:18:00
            "pickup_longitude": st.session_state.pickup_point['lon'] ,    # -73.950655
            "pickup_latitude": st.session_state.pickup_point['lat'] ,     # 40.783282
            "dropoff_longitude": st.session_state.dropoff_point['lon'] ,   # -73.984365
            "dropoff_latitude": st.session_state.dropoff_point['lat'] ,   # 40.769802
            "passenger_count": passenger_count       
        }
        try:
            response = requests.get(url, params=params, timeout=30)
            fare = response.json()
             
            st.sidebar.write(f"Estimated fare ${fare['fare']:.2f}")
        
        except requests.exceptions.ConnectionError as e:
            st.write(f"Connection error: {e}")
            # Check if it's a DNS issue
            if "[Errno -2]" in str(e):
                st.write("DNS resolution failed - check the domain name and network")
        except socket.gaierror as e:
            st.write(f"DNS error: {e}")
        except Exception as e:
            st.write(f"Other error: {e}")
