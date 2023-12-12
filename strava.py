import base64
import os

import arrow
import httpx
import streamlit as st
import sweat
from bokeh.models.widgets import Div

# APP_URL = st.secrets['APP_URL']
APP_URL = 'http://localhost:8501/'
STRAVA_CLIENT_ID = st.secrets['STRAVA_CLIENT_ID']
STRAVA_CLIENT_SECRET = st.secrets['STRAVA_CLIENT_SECRET']
STRAVA_AUTHORIZATION_URL = "https://www.strava.com/oauth/authorize"
STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
DEFAULT_ACTIVITY_LABEL = "NO_ACTIVITY_SELECTED"
STRAVA_ORANGE = "#fc4c02"

@st.cache_data(show_spinner=False)
# encoding of the loaded image
def load_image_as_base64(image_path):
    with open(image_path, "rb") as f:
        contents = f.read()
    return base64.b64encode(contents).decode("utf-8")

# authorization function - connecting to strava OAuth2
def authorization_url():
    request = httpx.Request(
        method="GET",
        url=STRAVA_AUTHORIZATION_URL,
        params={
            "client_id": STRAVA_CLIENT_ID,
            "redirect_uri": APP_URL,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": "activity:read_all"
        }
    )

    return request.url


def login_header(header=None):
    strava_authorization_url = authorization_url()

    if header is None:
        base = st
    else:
        col1, _, _, button = header
        base = button

    base64_image = load_image_as_base64("./images/connect_with_strava.png")
    base.markdown(
        (
            f"<a href=\"{strava_authorization_url}\">"
            f"  <img alt=\"strava login\" src=\"data:image/png;base64,{base64_image}\" width=\"100%\">"
            f"</a>"
        ),
        unsafe_allow_html=True,
    )

def logout_header(header=None):
    if header is None:
        base = st
    else:
        _, col2, _, button = header
        base = button

    if base.button("Log out"):
        js = f"window.location.href = '{APP_URL}'"
        html = f"<img src onerror=\"{js}\">"
        div = Div(text=html)
        st.bokeh_chart(div)


def logged_in_title(strava_auth, header=None):
    if header is None:
        base = st
    else:
        col, _, _, _ = header
        base = col

    first_name = strava_auth["athlete"]["firstname"]
    last_name = strava_auth["athlete"]["lastname"]
    col.markdown(f"*Welcome, {first_name} {last_name}!*")


@st.cache_data(show_spinner=False)
def exchange_authorization_code(authorization_code):
    response = httpx.post(
        url="https://www.strava.com/oauth/token",
        json={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
        }
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        st.error("Something went wrong while authenticating with Strava. Please reload and try again")
        st.experimental_set_query_params()
        st.stop()
        return

    strava_auth = response.json()

    return strava_auth


def authenticate(header=None, stop_if_unauthenticated=True):
    query_params = st.experimental_get_query_params()
    authorization_code = query_params.get("code", [None])[0]

    if authorization_code is None:
        authorization_code = query_params.get("session", [None])[0]

    if authorization_code is None:
        login_header(header=header)
        if stop_if_unauthenticated:
            st.stop()
        return
    else:
        logout_header(header=header)
        strava_auth = exchange_authorization_code(authorization_code)
        logged_in_title(strava_auth, header)
        st.experimental_set_query_params(session=authorization_code)

        return strava_auth


def header():
    col1, col2, col3 = st.columns(3)

    with col3:
        strava_button = st.empty()

    return col1, col2, col3, strava_button

# getting json data of 30 last activities
@st.cache_data(show_spinner=False)
def get_activities(auth, page=1):
    access_token = auth["access_token"]
    response = httpx.get(
        url=f"{STRAVA_API_BASE_URL}/athlete/activities",
        params={
            "page": page,
        },
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    return response.json()

#  activity lable for select box
def activity_label(activity):
    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        return ""

    start_date = arrow.get(activity["start_date_local"])
    human_readable_date = start_date.humanize(granularity=["day"])
    date_string = start_date.format("YYYY-MM-DD")

    return f"{activity['name']} - {date_string} ({human_readable_date})"


def select_strava_activity(auth):
    col1, col2 = st.columns([1, 3])
    with col1:
        page = st.number_input(
            label="Activities page",
            min_value=1,
            help="The Strava API returns your activities in chunks of 30. Increment this field to go to the next page.",
        )

    with col2:
        activities = get_activities(auth=auth, page=page)
        if not activities:
            st.info("This Strava account has no activities or you ran out of pages.")
            st.stop()
        default_activity = {"name": DEFAULT_ACTIVITY_LABEL, "start_date_local": ""}

        activity = st.selectbox(
            label="Select an activity",
            options=[default_activity] + activities,
            format_func=activity_label,
        )

    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        st.write("No activity selected")
        st.stop()
        return

    activity_url = f"https://www.strava.com/activities/{activity['id']}"
        
    st.markdown(
        f"<a href=\"{activity_url}\" style=\"color:{STRAVA_ORANGE};\">View on Strava</a>",
        unsafe_allow_html=True
    )

    return activity


def select_strava_activities(auth):
    col1, col2 = st.columns([1, 3])
    with col1:
        page = st.number_input(
            label="Activities page",
            min_value=1,
            help="The Strava API returns your activities in chunks of 30. Increment this field to go to the next page.",
        )

    with col2:
        activities = get_activities(auth=auth, page=page)
        if not activities:
            st.info("This Strava account has no activities or you ran out of pages.")
            st.stop()
        default_activity = {"name": DEFAULT_ACTIVITY_LABEL, "start_date_local": ""}

        activities = st.multiselect(
            label="Select an activity",
            options=[default_activity] + activities,
            format_func=activity_label,
        )

    return activities


@st.cache_data(show_spinner=False, max_entries=30)
def download_activity(activity, strava_auth):
    with st.spinner(f"Downloading activity \"{activity['name']}\"..."):
        return sweat.read_strava(activity["id"], strava_auth["access_token"])

@st.cache_data(show_spinner=False, max_entries=30)
def download_activities(activities, strava_auth):
    activities_number = len(activities)
    activity_data_list = []
    for activity_number in range(0, activities_number):
        activity = sweat.read_strava(activities[activity_number]["id"], strava_auth["access_token"])
        activity_data_list.append(activity)
    with st.spinner(f"Downloading activities..."):
        return activity_data_list
