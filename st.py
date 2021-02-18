import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import requests
import urllib.parse

def get_data():
    data = requests.get("https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%7D")
    return json.loads(data.text) 

@st.cache(ttl=60*60)
def data_process():
    for content in building_list:
        content["address"] = content["Building name"].replace("(non-residential)", "")
        content["address"] = content["address"].replace("%", "")
        content["address"] = urllib.parse.quote(content["address"])
        name = content["address"]
        location_file = requests.get(f"https://geodata.gov.hk/gs/api/v1.0.0/locationSearch?q={name}")
        location_file = json.loads(location_file.text)
        x = location_file[0]["x"]
        y = location_file[0]["y"]
        convert = requests.get(f"http://www.geodetic.gov.hk/transform/v2/?inSys=hkgrid&outSys=wgsgeog&e={x}&n={y}")
        converted = json.loads(convert.text)
        content["Lat"] = converted["wgsLat"]
        content["Long"] = converted["wgsLong"]
    return building_list

def map_loading():
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position="[Long, Lat]",
        auto_highlight=True,
        get_radius=100,
        get_fill_color=[180, 0, 200, 140],
        pickable=True)

    tooltip={
        "html": "{Building name}<br>Related Cases: {Related probable/confirmed cases}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    a = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        layers=[layer],
        #api_keys={"mapbox":MAPBOX_API_KEY},
        #map_style='light',
        initial_view_state={"latitude":22.35, "longitude":114.15, "zoom":9.5},
        #map_provider="mapbox",
        tooltip=tooltip)
    
    return a

building_list = get_data()
df = pd.DataFrame(data_process())
st.write("""
HK COVID Map\n
Residential buildings in which probable/confirmed cases have resided in the past 14 days or non-residential building with 2 or more probable/confirmed cases in the past 14 days
""")
st.pydeck_chart(map_loading())