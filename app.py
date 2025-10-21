import streamlit as st
import time
import os
import logging
import warnings

import pandas as pd
import nflreadpy as nfl
from supabase import create_client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor


# Most useful column from massive live play_by_play dataset
# Cuts down from 300+ to 38
keep_cols = [
    # Identifiers (2)
    'play_id',        # Unique ID for each play (needed for timeline clicks)
    'game_id',        # Unique ID for each game
    
    # Game Info (5)
    'home_team',      # Home team abbreviation (e.g., "KC", "SF")
    'away_team',      # Away team abbreviation
    'week',           # Week number (1-18)
    'season',         # Year (e.g., 2024)
    'game_date',      # Date of game
    
    # Situation (11)
    'qtr',            # Quarter (filter to 4 for 4th quarter only)
    'game_seconds_remaining',  # Seconds left in entire game (3600 = start, 0 = end)
    'down',           # Down (1, 2, 3, 4)
    'ydstogo',        # Yards to go for first down
    'goal_to_go',     # Boolean: is it goal-to-go situation?
    'yardline_100',   # DISTANCE TO OPPONENT'S END ZONE (25 = own 25, 75 = opp 25, 10 = opp 10)
    'posteam',        # Team with possession (offense)
    'defteam',        # Team on defense
    'posteam_score',  # Possession team's score
    'defteam_score',  # Defense team's score
    'score_differential',  # Posteam score minus defteam score (positive = winning)
    
    # Play Details (9)
    'desc',           # Full play description text (for display to user)
    'play_type',      # Type: run, pass, punt, field_goal, kickoff, etc.
    'yards_gained',   # Yards gained on the play (negative = loss)
    'touchdown',      # Boolean: was it a TD?
    'pass_touchdown', # Boolean: passing TD?
    'rush_touchdown', # Boolean: rushing TD?
    'field_goal_result',  # Result: made, missed, blocked
    'extra_point_attempt', # Boolean: was this an XP attempt?
    'two_point_attempt',   # Boolean: was this a 2PT attempt?
    
    # Clock Management (9)
    'play_clock',     # Seconds consumed by this play
    'no_huddle',      # Boolean: no-huddle offense?
    'qb_kneel',       # Boolean: QB kneel (clock killer)
    'qb_spike',       # Boolean: QB spike (clock stopper)
    'timeout',        # Boolean: was timeout called?
    'timeout_team',   # Which team called timeout
    'posteam_timeouts_remaining',  # Offense timeouts left
    'defteam_timeouts_remaining',  # Defense timeouts left
    'out_of_bounds',  # Boolean: did ball carrier go out of bounds? (stops clock)
    
    # Additional Context (2)
    'incomplete_pass', # Boolean: incomplete pass (stops clock)
    'sack',           # Boolean: QB sacked
    'penalty'         # Boolean: penalty on play (affects clock)
]


# Gets current NFL season
current_season = nfl.get_current_season()

# Loads current season NFL play_by_play data
pbp_data = nfl.load_pbp(
  seasons = current_season
)

print(type(pbp_data))

# Convert from polars to pandas
df = pbp_data.to_pandas()

print(f"Original data: {df.shape[0]} rows, {df.shape[1]} columns")

# Filter to 4th quarter only AND keep only selected columns
print("Filtering to 4th quarter and selected columns...")
df_filtered = df[df['qtr'] == 4][keep_cols]

print(f"Filtered data: {df_filtered.shape[0]} rows, {df_filtered.shape[1]} columns")

# Save the filtered CSV
df_filtered.to_csv('pbp_4th_quarter_clean.csv', index=False)
print("✅ Saved filtered data to pbp_4th_quarter_clean.csv")


load_dotenv() # Loads values from env file

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)


# Quick check to see if can connect to Supabase database
response = supabase.table('Teams').select("*").execute()

print(response)

current_season = nfl.get_current_season()

current_week = nfl.get_current_week()

print(f"It is the {current_season} season and its week {current_week}")

