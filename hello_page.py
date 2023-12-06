import streamlit as st
import os
import strava

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

    [Contact me](sebastian.konicz@gmail.com) if you have any suggestions.
    
    Project inspired and partialy based on project of Aart Goossens  [GitHub](https://github.com/AartGoossens/streamlit-activity-viewer)
    """
)

strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)