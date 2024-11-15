import altair as alt
import streamlit as st
import strava
import pandas as pd

st.set_page_config(
    page_title="Strava HR Zones",
    page_icon='heart',
    )

strava_header = strava.header()

st.markdown(
    "<h1 style='text-align: center;'>Strava HR Zones Viewer </h1>", unsafe_allow_html=True
)
st.markdown(
    """
    ### :heart::running: :bicyclist::heart:
    This is a proof of concept of a [Streamlit](https://streamlit.io/) application that implements the [Strava API](https://developers.strava.com/) OAuth2 authentication flow.
    """
)

strava_auth = strava.authenticate(header=strava.header(), stop_if_unauthenticated=False)

if strava_auth is None:
    st.markdown("Click the \"Connect with Strava\" button at the top to login with your Strava account and get started.")
    st.stop()

# activity = strava.select_strava_activity(strava_auth)
# data = strava.download_activity(activities, strava_auth)

# getting activities
page = strava.select_page()
print(page)
activities = strava.select_strava_activities(strava_auth, page)
# sport_list = strava.select_sport()
sport_list_amd = strava.select_sport_amd(activities)
data_list = strava.download_activities(activities, sport_list_amd, strava_auth)

# setting zone values
zones = strava.get_hr_zones(strava_auth, page=1)
z1_max = zones["heart_rate"]["zones"][0]['max']
z2_max = zones["heart_rate"]["zones"][1]['max']
z3_max = zones["heart_rate"]["zones"][2]['max']
z4_max = zones["heart_rate"]["zones"][3]['max']

# st.json(zones)
# st.markdown(zones["heart_rate"]["zones"])
# st.markdown(z1_max)

# zones dataframe
data = {
    'zone': ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'],
    'zone name': ['Endurance', 'Moderate', 'Tempo', 'Threshold', 'Anaerobic'],
    'zone hr range': [f'< {z1_max}', f'{z1_max} - {z2_max} ', f'{z2_max} - {z3_max}', f'{z3_max} - {z4_max}', f'> {z4_max}']
}

zones_df = pd.DataFrame(data)
# st.dataframe(zones_df, hide_index=True, use_container_width=False)

# getting zones
# seconds in hr zones
def hr_zones(value, z1=z1_max, z2=z2_max, z3=z3_max, z4=z4_max):
    if value <= z1:
        zone = 'Z1'
    elif (value > z1) & (value <= z2):
        zone = 'Z2'
    elif (value > z2) & (value <= z3):
        zone = 'Z3'
    elif (value > z3) & (value <= z4):
        zone = 'Z4'
    elif value > z4:
        zone = 'Z5'
    return zone

zone_aggregations = []
for activity in data_list:
    # calculating secconds diffrence based on datetime index
    activity['seconds'] = activity.index.to_series().diff().dt.total_seconds().fillna(0)
    # activity['seconds'].fillna(0, inplace=True) # chek if redundant

    activity['zone'] = activity.apply(lambda x: hr_zones(x['heartrate']), axis=1)
    zone_data = pd.DataFrame(activity.groupby("zone")['seconds'].sum()).reset_index().copy()
    zone_aggregations.append(zone_data)

# concatenation of activites per zone
if len(zone_aggregations) != 0:
    concat = pd.concat(zone_aggregations)

    # getting combined time in seconds
    concat_aggr = pd.DataFrame(concat.groupby("zone")['seconds'].sum()).reset_index()
    zones_df = zones_df.merge(concat_aggr, how='left', on='zone')

    # fillng blank data
    zones_df['seconds'].fillna(value=0, inplace=True)

    # calculating percent time
    total_seconds = zones_df['seconds'].sum()
    zones_df['percent'] = round((zones_df['seconds'] / total_seconds) * 100, 2)

    # formating data
    zones_df['time'] = pd.to_timedelta(zones_df['seconds'], unit='s').apply(lambda x: str(x))

    # restricting dataframe to useful columns in correct order
    zones_df = zones_df[['zone', 'zone name', 'zone hr range', 'time', 'seconds', 'percent']]
    zones_df.rename(columns={'seconds': "time [seconds]", "percent": "% share"}, inplace=True)

    st.dataframe(zones_df, hide_index=True, use_container_width=False)

    # wykres
    altair_chart = alt.Chart(zones_df).mark_bar(color=strava.STRAVA_ORANGE).encode(
        y="zone",
        x="% share"
    ).properties(height=500)  # zwiększenie wysokości wykresu

    # tekst na wykresie
    text = altair_chart.mark_text(
        align='left',
        baseline='middle',
        dx=3 #przesuniecie w prawo o 3 piksele
    ).encode(text='% share:Q')

    st.altair_chart(altair_chart + text, use_container_width=True)

else:
    pass

st.markdown(
    """
    ---------------------------
    \nThe source code can be found at [my GitHub](https://github.com/sebastian-konicz/strava-hr-zones) and is licensed under an [MIT license](https://github.com/sebastian-konicz/strava-hr-zones/blob/main/LICENSE).
    \nContact me if you have any suggestions: sebastian.konicz@gmail.com.
    \nProject inspired and partialy based on  Aart Goossens's project [GitHub](https://github.com/AartGoossens/streamlit-activity-viewer)
    """
)