import streamlit as st
import time
import warnings
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

from config import nfl, pd, logging, os, get_supabase_client, get_current_season, get_current_week
import play_by_play_database_setup as pbp_db_setup

st.set_page_config("NFL 4th Quarter Offensive Decision Analyzer")

logging.basicConfig (
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Suppress Long HTTP logs (set DEBUG_HTTP=true in .env to see all HTTP logs)
if not os.getenv("DEBUG_HTTP"):
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

ESPN_LOGO_TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"


# Prepares play_by_play data to be sent over to supabase database
df = pbp_db_setup.setup_data_for_database()

# Sends over play_by_play data to be sent over to supabase database
# Updates if new info is present
# Using batch inserts 1000 rows per batch
pbp_db_setup.database_upload_play_by_play_data(df)


current_season = get_current_season()
current_week = get_current_week()
logging.info(f"\nIt is the {current_season} season and its week {current_week}")


# Cache for 24 hours
@st.cache_data(ttl=86400)
def get_nfl_team_logos():
    # Fetch ESPN DATA
    response = requests.get(ESPN_LOGO_TEAMS_URL, timeout=10)
    # Convert to JSON
    data = response.json()

    # To see structure of API resposnse
    # with open("data/ESPN_LOGO_TEAMS.json", "w") as f:
    #     json.dump(data, f, indent=2)

    # Navigate to teams
    teams = data["sports"][0]["leagues"][0]["teams"]
    
    nfl_logos = {}

    # Loop and extract
    for team in teams:
        team_abbreviation = team["team"]["abbreviation"]
        nfl_logos[team_abbreviation] = team["team"]["logos"][0]["href"]

    return nfl_logos

# logging.info(get_nfl_team_logos())


# Fetch all the games current week

schedule = nfl.load_schedules(current_season)

df_schedule = schedule.to_pandas()

df_schedule.to_csv('data/nfl_schedule.csv', index=False)

logging.info(type(df_schedule))


date = st.date_input("Whats the date today")

st.write(date)

# Store into new table (game_schedule_and_past_scores) database

