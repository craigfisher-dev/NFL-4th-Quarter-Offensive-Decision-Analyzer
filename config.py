import nflreadpy as nfl
import pandas as pd
import logging
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables once
load_dotenv()

# Create Supabase client once (reusable)
def get_supabase_client():
    """Returns configured Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

# Get current season once (can be reused)
def get_current_season():
    return nfl.get_current_season()

def get_current_week():
    return nfl.get_current_week()