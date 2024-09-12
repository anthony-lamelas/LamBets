from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams
import pandas as pd

# Get all NBA teams
team_dict = teams.get_teams()

# Fetch base stats for all teams in the season
league_stats_base = leaguedashteamstats.LeagueDashTeamStats(
    season='2013-14',
    season_type_all_star='Regular Season',  # Regular season data
    measure_type_detailed_defense='Base',   # Base stats (points, rebounds, assists, etc.)
    per_mode_detailed='PerGame'             # Per game stats
)

# Fetch advanced stats for all teams in the season
league_stats_advanced = leaguedashteamstats.LeagueDashTeamStats(
    season='2013-14',
    season_type_all_star='Regular Season',  # Regular season data
    measure_type_detailed_defense='Advanced',  # Advanced stats (offensive rating, defensive rating, etc.)
    per_mode_detailed='PerGame'             # Per game stats
)

# Convert both results to pandas DataFrames
df_base_stats = league_stats_base.get_data_frames()[0]
df_advanced_stats = league_stats_advanced.get_data_frames()[0]

# Merge base and advanced
df_combined_stats = pd.merge(df_base_stats, df_advanced_stats, on='TEAM_ID', suffixes=('_base', '_advanced'))

# Dataframe head
print("Comprehensive Team Stats for the 2013-14 NBA Season:")
print(df_combined_stats.head())

# Save the DataFrame to a CSV file 
df_combined_stats.to_csv('nba_team_stats_2013-14.csv', index=False)





