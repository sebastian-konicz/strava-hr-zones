import base64
import altair as alt
import streamlit as st
import os
import strava
import pandas as pd
from pandas.api.types import is_numeric_dtype

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
activities = strava.select_strava_activities(strava_auth)
data_list = strava.download_activities(activities, strava_auth)

# getting zones
# seconds in hr zones
def zones(value):
    if value <= 110:
        zone = 'endurance'
    elif (value > 110) & (value <= 145):
        zone = 'moderate'
    elif (value > 145) & (value <= 163):
        zone = 'temp'
    elif (value > 163) & (value <= 181):
        zone = 'treshold'
    elif value > 181:
        zone = 'anaerobic'
    return zone

zone_aggregations = []
for activity in data_list:
    activity['seconds'] = 1
    activity['zone'] = activity.apply(lambda x: zones(x['heartrate']), axis=1)
    zone_data = pd.DataFrame(activity.groupby("zone")['seconds'].sum()).reset_index()
    zone_aggregations.append(zone_data)

# concatenation of activites per zone
concat = pd.concat(zone_aggregations)

concat_aggr = pd.DataFrame(activity.groupby("zone")['seconds'].sum()).reset_index()

st.dataframe(concat_aggr)
