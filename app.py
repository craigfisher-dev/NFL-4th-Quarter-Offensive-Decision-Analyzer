import streamlit as st
import time
import os
import logging
import warnings

import nflreadpy as nfl
from supabase import create_client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor




load_dotenv() # Loads values from env file

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)


# Quick check to see if can connect to Supabase database
response = supabase.table('Teams').select("*").execute()

print(response)


player_rankings = nfl.load_ff_rankings("week")

current_season = nfl.get_current_season()

current_week = nfl.get_current_week()

print(f"It is the {current_season} season and its week {current_week}")


# Outputs file to new CV file
player_rankings.write_csv('player_rankings.csv')
