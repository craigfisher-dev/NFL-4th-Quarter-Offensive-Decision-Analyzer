# NFL 4th Quarter Time Management Analyzer

**Live App**: [Coming Soon - Deploy URL Here]

Evaluates NFL team decision-making in critical 4th quarter situations based on game context, time remaining, and score differential. Analyzes whether teams make optimal play-calling choices when protecting leads versus needing to score quickly. Built with Python, Streamlit, nfl_data_py, and hosted on Render.

## Features
- Team-specific 4th quarter decision analysis
- Run/pass ratio evaluation based on game situation (leading vs trailing)
- Decision quality grading system
- League-wide time management rankings
- Daily updates with latest completed games
- Situational breakdowns with strategic recommendations

## How It Works
The analyzer examines every 4th quarter play to determine if teams made strategically sound decisions. When protecting a lead, smart teams run the ball to consume clock time. When trailing and needing to score, effective teams pass aggressively to preserve time. Each team receives grades based on their decision-making patterns, with rankings showing which coaches manage the clock best in pressure situations.

## Key Metrics
- **When Leading**: Run percentage (higher is better - kills clock)
- **When Trailing**: Pass percentage (higher is better - saves time)
- **Time Management Score**: Combined rating of situational decision quality
- **Decision Grades**: Contextual evaluation (Good/OK/Bad) based on game situation

## Tech Stack
- **Backend**: Python, Pandas
- **Frontend**: Streamlit
- **Data Source**: nflreadpy (NFL current data)
- **Hosting**: Render
- **Updates**: Daily after completed games

## Data Processing
- Filters play-by-play data to 4th quarter situations only
- Calculates score differential to determine leading/trailing status
- Analyzes run vs pass tendencies by game context
- Evaluates strategic appropriateness of play-calling decisions
- Generates team rankings based on time management effectiveness
- Updates automatically with latest season data from completed games