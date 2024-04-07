import base64
import altair as alt
import streamlit as st
import os
import strava
import pandas as pd
import datetime as dt
from pandas.api.types import is_numeric_dtype
from pandas.io.json import json_normalize

cwd = os.getcwd()

st.set_page_config(
    page_title="Strava HR Zones",
    page_icon='heart',
    )

strava_header = strava.header()

st.markdown(
    """
    ### :heart: :running: Streamlit Strava HR Zones Viever :bicyclist: :heart:
    This is a proof of concept of a [Streamlit](https://streamlit.io/) application that implements the [Strava API](https://developers.strava.com/) OAuth2 authentication flow.
    The source code can be found at [my GitHub](https://github.com/sebastian-konicz/strava-hr-zones) and is licensed under an [MIT license](https://github.com/sebastian-konicz/strava-hr-zones/blob/main/LICENSE).

    Contact me if you have any suggestions: sebastian.konicz@gmail.com.
    
    Project inspired and partialy based on project of Aart Goossens  [GitHub](https://github.com/AartGoossens/streamlit-activity-viewer)
    """
)

strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)

if strava_auth is None:
    st.markdown("Click the \"Connect with Strava\" button at the top to login with your Strava account and get started.")
    st.stop()

# activity = strava.select_strava_activity(strava_auth)
# data = strava.download_activity(activities, strava_auth)

# getting activities
sport_list = strava.select_sport()
activities = strava.select_strava_activities(strava_auth)
data_list = strava.download_activities(activities, sport_list, strava_auth)

zones = strava.get_hr_zones(strava_auth, page=1)
st.json(zones)
# zones = json_normalize(zones)

st.markdown(zones["heart_rate"]["zones"])
z1_max = zones["heart_rate"]["zones"][0]['max']
z2_max = zones["heart_rate"]["zones"][1]['max']
z3_max = zones["heart_rate"]["zones"][2]['max']
z4_max = zones["heart_rate"]["zones"][3]['max']
st.markdown(z1_max)

# getting zones
# seconds in hr zones
def hr_zones(value, z1=z1_max, z2=z2_max, z3=z3_max, z4=z4_max):
    if value <= z1:
        zone = 'Z1: endurance'
    elif (value > z1) & (value <= z2):
        zone = 'Z2: moderate'
    elif (value > z2) & (value <= z3):
        zone = 'Z3: tempo'
    elif (value > z3) & (value <= z4):
        zone = 'Z4: treshold'
    elif value > z4:
        zone = 'Z5: anaerobic'
    return zone

zone_aggregations = []
for activity in data_list:
    # calculating secconds diffrence based on datetime index
    activity['seconds'] = activity.index.to_series().diff().dt.total_seconds()
    activity['seconds'].fillna(0, inplace=True)
    activity['zone'] = activity.apply(lambda x: hr_zones(x['heartrate']), axis=1)
    zone_data = pd.DataFrame(activity.groupby("zone")['seconds'].sum()).reset_index().copy()
    zone_aggregations.append(zone_data)

# concatenation of activites per zone
if len(zone_aggregations) != 0:
    concat = pd.concat(zone_aggregations)
    # getting combined time in seconds
    concat_aggr = pd.DataFrame(concat.groupby("zone")['seconds'].sum()).reset_index()
    # calculating percent time
    total_seconds = concat_aggr['seconds'].sum()
    concat_aggr['percent'] = round((concat_aggr['seconds'] / total_seconds) * 100, 2)

    st.dataframe(concat_aggr)

    altair_chart = alt.Chart(concat_aggr).mark_bar(color=strava.STRAVA_ORANGE).encode(
        x="zone",
        y="percent"
    )
    st.altair_chart(altair_chart, use_container_width=True)
else:
    pass
