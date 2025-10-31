import streamlit as st
import time
import os
import logging
import warnings
import requests
import json

import pandas as pd
import nflreadpy as nfl
from supabase import create_client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

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

# Most useful column from massive live play_by_play dataset
# Cuts down from 300+ to 38
keep_cols = [
    # Identifiers (2)
    'play_id',        # Unique ID for each play (needed for timeline clicks)   (Type in database: float4)
    'game_id',        # Unique ID for each game (Type in database: text)
    
    # Game Info (5)
    'home_team',      # Home team abbreviation (e.g., "KC", "SF") (Type in database: text)
    'away_team',      # Away team abbreviation (Type in database: text)
    'week',           # Week number (1-18) (Type in database: int2)
    'season',         # Year (e.g., 2024) (Type in database: int2)
    'game_date',      # Date of game (Type in database: date)
    'start_time',     # Actual game kickoff time (for sorting games by time slot) (Type in database: timestamptz)
    
    # Situation (11)
    'qtr',            # Quarter (filter to 4 for 4th quarter only) (Type in database: float4)
    'game_seconds_remaining',  # Seconds left in entire game (3600 = start, 0 = end) (Type in database: float4)
    'down',           # Down (1, 2, 3, 4) (Type in database: float4)
    'ydstogo',        # Yards to go for first down (Type in database: float4)
    'goal_to_go',     # Is it goal-to-go situation? (1 = yes)   (0 = no)    (Type in database: int2)
    'yardline_100',   # DISTANCE TO OPPONENT'S END ZONE (25 = own 25, 75 = opp 25, 10 = opp 10) (Type in database: float4)
    'posteam',        # Team with possession (offense) (Type in database: text)
    'defteam',        # Team on defense (Type in database: text)
    'posteam_score',  # Possession team's score (Type in database: float4)
    'defteam_score',  # Defense team's score (Type in database: float4)
    'score_differential',  # Posteam score minus defteam score (positive = winning) (Type in database: float4)
    
    # Play Details (9)
    'desc',           # Full play description text (for display to user) (Type in database: text)
    'play_type',      # Type: run, pass, punt, field_goal, kickoff, etc. (Type in database: text)
    'yards_gained',   # Yards gained on the play (negative = loss) (Type in database: float4)
    'touchdown',      # Was it a TD?  (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'pass_touchdown', # Passing TD?   (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'rush_touchdown', # Rushing TD?   (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'field_goal_result',  # Result: made, missed, blocked (Type in database: text)
    'extra_point_attempt', # Was this an XP attempt? (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'two_point_attempt',   # Was this a 2PT attempt? (1.0 = yes)   (0.0 = no) (Type in database: float4)
    
    # Clock Management (8)
    'no_huddle',      # No-huddle offense?        (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'qb_kneel',       # QB kneel (clock killer)   (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'qb_spike',       # QB spike (clock stopper)  (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'timeout',        # Was timeout called?       (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'timeout_team',   # Which team called timeout (Type in database: text)
    'posteam_timeouts_remaining',  # Offense timeouts left (Either 3.0, 2.0, 1.0, 0.0) (Type in database: float4)
    'defteam_timeouts_remaining',  # Defense timeouts left (Either 3.0, 2.0, 1.0, 0.0) (Type in database: float4)
    'out_of_bounds',  # Did ball carrier go out of bounds? (stops clock) (1.0 = yes)   (0.0 = no) (Type in database: float4)
    
    # Additional Context (2)
    'incomplete_pass', # Incomplete pass (stops clock) (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'sack',           # QB sacked (1.0 = yes)   (0.0 = no) (Type in database: float4)
    'penalty'         # Penalty on play (1.0 = yes)   (0.0 = no) (affects clock) (Type in database: float4)
]


# Gets current NFL season
current_season = nfl.get_current_season()

# Loads current season NFL play_by_play data
pbp_data = nfl.load_pbp(
  seasons = current_season
)

# Convert from polars to pandas
df = pbp_data.to_pandas()

# Filter to 4th quarter only AND keep only selected columns
logging.info("Filtering to 4th quarter and selected columns...")
df_filtered = df[df['qtr'] == 4][keep_cols].copy()

logging.info(f"Filtered data: {df_filtered.shape[0]} rows, {df_filtered.shape[1]} columns")

# Convert start_time to proper datetime format
logging.info("Converting start_time to datetime format...")
df_filtered['start_time'] = pd.to_datetime(df_filtered['start_time'], errors='coerce')

logging.info("Sorting data chronologically...")
df_filtered = df_filtered.sort_values(
    by=['game_date', 'start_time', 'game_id', 'game_seconds_remaining'],
    ascending=[True, True, True, False]  # False for game_seconds because it counts DOWN
).reset_index(drop=True)



# Save the filtered CSV
df_filtered.to_csv('pbp_4th_quarter_clean.csv', index=False)
logging.info("✅ Saved filtered data to pbp_4th_quarter_clean.csv")


load_dotenv() # Loads values from env file

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# Upload data to Supabase
logging.info("\nUploading data to Supabase...")


# Convert DataFrame to list of dictionaries
plays = df_filtered.to_dict('records')


# Handle NaN/None values and convert datetime to ISO string for Supabase
for play in plays:
    # Go through each column in this play (38 total columns)
    # Makes a copy with list() so we can safely change values while looping
    for column_name, column_value in list(play.items()):
        
        # If the value is missing (NaN), change it to None for the database
        if pd.isna(column_value):
            play[column_name] = None
        # If the value is a datetime, convert it to a text string
        elif isinstance(column_value, pd.Timestamp):
            play[column_name] = column_value.isoformat()  # Convert datetime to ISO string


# Upload in batches using upsert (Supabase recommend 1000 rows per batches)
batch_size = 1000
total_records = len(plays)
batch_number = 1

for i in range(0, total_records, batch_size):
    # Get the next 1000 plays
    batch = plays[i:i + batch_size]

    # Try to upload this batch
    try:
        response = supabase.table('play_by_play').upsert(batch, on_conflict='game_id,play_id').execute()
        logging.info(f"✅ Uploaded batch {batch_number}: {len(batch)} records")
    except Exception as e:
        logging.error(f"❌ Error uploading batch {batch_number}: {e}")
    batch_number += 1

logging.info(f"\n✅ Finished uploading {total_records} records to Supabase")


# No need to worry about id size getting big becuase an int8 is about 9,000,000,000,000,000,000
# So if it auto increments by about 35000 everytime it updates (Which will be a few times per day)
# It will take a really long time to reach unwanted behavior :D 

# Testing data upserting a single row after big batch upsert 
# response = supabase.table('play_by_play').upsert(({'game_id': '99999999999989', 'play_id': '9999999979999999'}), on_conflict='game_id,play_id').execute()


current_season = nfl.get_current_season()
current_week = nfl.get_current_week()
logging.info(f"\nIt is the {current_season} season and its week {current_week}")



# Cache for 24 hours
@st.cache_data(ttl=86400)
def get_nfl_team_logos():
    # Fetch ESPN DATA
    response = requests.get(ESPN_LOGO_TEAMS_URL, timeout=10)
    # Convert to JSON
    data = response.json()

    # To see structure of API resposnse
    # with open("ESPN_LOGO_TEAMS.json", "w") as f:
    #     json.dump(data, f, indent=2)

    # Navigate to teams
    teams = data["sports"][0]["leagues"][0]["teams"]
    
    nfl_logos = {}

    # Loop and extract
    for team in teams:
        team_abbreviation = team["team"]["abbreviation"]
        nfl_logos[team_abbreviation] = team["team"]["logos"][0]["href"]

    return nfl_logos

logging.info(get_nfl_team_logos())