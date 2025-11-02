from config import nfl, pd, logging, get_supabase_client, get_current_season


def setup_schedule_data_database(current_season):
    
    # Most useful column from nfl_schedule dataset
    keep_cols = [
        # Identifiers (2)
        'game_id',        # Unique ID for each game (matches play_by_play data) (Type: text)
        'season',         # Year (e.g., 2025) (Type: int2)
        
        # Game Scheduling (5)
        'game_type',      # Type: REG (Regular_Season_Game), WC (Wildcard_Game),
                          # DIV (Divisional_Game), CON (Conference_Championship) (Type: text)

        'week',           # Week number (1-18 for regular season) (19-22 for post season) (Type: int2)
        'gameday',        # Date of game (YYYY-MM-DD format) (Type: date)
        'weekday',        # Day of week (Thursday, Sunday, Monday, etc.) (Type: text)
        'gametime',       # Scheduled kickoff time (HH:MM format) (Type: text)
        
        # Teams (2)
        'away_team',      # Away team abbreviation (e.g., "KC", "SF") (Type: text)
        'home_team',      # Home team abbreviation (Type: text)
        
        # Game Results (3)
        'away_score',     # Final score for away team (Type: float4)
        'home_score',     # Final score for home team (Type: float4)
        'result',         # Point differential (home_score - away_score) (Type: float4)
        
        # Additional Info (2)
        'overtime',       # Did game go to OT? (1.0 = yes, 0.0 = no) (Type: float4)
        'stadium',        # Stadium name where game was played (Type: text)
    ]

    # Fetch all the games current week
    schedule = nfl.load_schedules(current_season)

    # Convert from polars to pandas
    df_schedule = schedule.to_pandas()

    # Filter to keep only selected columns
    logging.info("Filtering to selected columns...")
    df_schedule_filtered = df_schedule[keep_cols].copy()

    logging.info("Sorting data chronologically...")
    df_schedule_filtered = df_schedule_filtered.sort_values(
        by=['gameday', 'gametime'],
        ascending=[True, True] 
    ).reset_index(drop=True)

    df_schedule_filtered.to_csv('data/nfl_schedule_clean.csv', index=False)

    logging.info(type(df_schedule_filtered))

    # Convert DataFrame to list of dictionaries
    games = df_schedule_filtered.to_dict('records')

    for game in games:
        # Go through each column in this game (14 total columns)
        # Makes a copy with list() so we can safely change values while looping
        for column_name, column_value in list(game.items()):
            
            # If the value is missing (NaN), change it to None for the database
            if pd.isna(column_value):
                game[column_name] = None
    
    return games

def database_upload_schedule_data(games):
    # Upload data to Supabase
    logging.info("\nUploading schedule_data to Supabase...")

    # Connects to Supabase Database   (Funciton in config.py)
    supabase = get_supabase_client()

    # Upload in batches using upsert (Supabase recommend 1000 rows per batches)
    batch_size = 1000
    total_records = len(games)
    batch_number = 1

    for i in range(0, total_records, batch_size):
        # Get the next 1000 games (There are not 1000 games in a season,
        # but we can do it all in one batch)
        batch = games[i:i + batch_size]

        # Try to upload this batch
        try:
            response = supabase.table('game_schedule_and_past_scores').upsert(batch, on_conflict='game_id').execute()
            logging.info(f"✅ Uploaded batch {batch_number}: {len(batch)} records")
        except Exception as e:
            logging.error(f"❌ Error uploading batch {batch_number}: {e}")
        batch_number += 1

    # Note

    # No need to worry about id size getting big becuase an int8 is about 9,000,000,000,000,000,000
    # So if it auto increments by about 35000 everytime it updates (Which will be a few times per day)
    # It will take a really long time to reach unwanted behavior :D 

    logging.info(f"\n✅ Finished uploading {total_records} records to Supabase")

    return

# Note:

# Wherever games will be displayed:
# response = supabase.table('game_schedule_and_past_scores') \
#     .select('*') \
#     .order('gameday') \
#     .order('gametime') \
#     .execute()

# games = response.data  # Sorted for users