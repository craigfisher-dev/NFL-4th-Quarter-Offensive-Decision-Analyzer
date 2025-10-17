# NFL 4th Quarter Offensive Decision Analyzer

**Live App**: [Coming Soon - Deploy URL Here]

Tells NFL offenses the exact decision they SHOULD make in any 4th quarter situation to maximize win probability. Analyzes game context (score, time, field position) and recommends RUN, PASS, PUNT, FIELD GOAL, EXTRA POINT, or GO FOR 2 with clear explanations of clock impact and strategic reasoning. Built with Python, Streamlit, nflreadpy, Supabase, and hosted on Render.


**Core Philosophy**: 
- **When leading**: Kill the clock with smart decisions
- **When trailing by one score**: Control the clock and score methodically while denying your opponent time to answer back
- **When trailing by multiple scores**: Maximize possessions by getting plays off quickly and scoring fast to create multiple comeback opportunities

## Features

### Game Selection & Visualization
- **NFL game browser** - Search and select any game from the current season by week, team, or date
- **Visual football field** - Visual field diagram showing ball position, yard lines, end zones (with team names), line of scrimmage (blue line), first down line (yellow line)
- **Live situation display** - Real-time view of down, distance, yards to first down, field position, score differential, and time remaining
- **4th quarter timeline** - Scrub through every play (show play-by-play on side user can click on it to jump to any play) in the 4th quarter with instant situation updates

### Decision Analysis (Live / Complete Games)
- **Six decision types** - RUN, PASS, PUNT, FIELD GOAL, EXTRA POINT, GO FOR 2
- **Optimal play recommendations** - AI-driven suggestions for the best decision in each moment
- **Clock management analysis**
  - Tracks actual time consumed by completed plays
  - Calculates maximum clock burn for runs (staying inbounds, running clock down between plays)
  - Analyzes strategic clock plays: kneel downs to burn time, spikes to stop clock
  - Analyzes clock impact of passes (incompletions stop clock, inbounds catches burn clock)
  - Evaluates strategic choices: staying inbounds vs going out of bounds
  - Shows time consumed by punts, field goal attempts, and kickoffs (normal and onside)
  - Notes PAT and 2PT conversion attempts (no clock impact)
  - Identifies all clock events (timeouts, penalties, two-minute warning)
- **Strategic explanations** - Clear, detailed reasoning for every recommendation with situational context

### Historical Analysis (Complete Game)
- **Actual vs optimal comparison** - Side-by-side view of what teams called versus what they should have called
- **Critical moment breakdowns** - Point out (Orange in play-by-play timeline) critical errors in game and how they can be avoided


### Data Infrastructure
- **Automatic updates** - Database refreshes with new games as they complete
- **Cloud storage** - All play-by-play data, recommendations, and analytics stored in Supabase
- **Complete archive** - Full historical record of all games, plays, and decisions for current season, plus a few hand picked fun games to analyze from the past

**Note**: Database storage is limited to 0.5 GB - only storing 4th quarter plays and essential game data to optimize space usage