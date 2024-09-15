from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueGameLog
from Major_Injury import *
import pandas as pd

# Get all NBA teams
team_dict = teams.get_teams()

league_stats_base = leaguedashteamstats.LeagueDashTeamStats(
    season='2016-17',
    season_type_all_star='Regular Season',  
    measure_type_detailed_defense='Base',   
    per_mode_detailed='PerGame'            
)

# Fetch advanced stats for all teams in the season
league_stats_advanced = leaguedashteamstats.LeagueDashTeamStats(
    season='2016-17',
    season_type_all_star='Regular Season',  
    measure_type_detailed_defense='Advanced',  
    per_mode_detailed='PerGame'            
)

# Convert both results to pandas DataFrames
df_base_stats = league_stats_base.get_data_frames()[0]
df_advanced_stats = league_stats_advanced.get_data_frames()[0]


df_combined_stats = pd.merge(df_base_stats, df_advanced_stats, on='TEAM_ID', suffixes=('_base', '_advanced'))

#Player Data

# Step 1: Pull game-level player data for a specific season
def get_player_game_log(season):
    game_log = LeagueGameLog(season=season, player_or_team_abbreviation='P').get_data_frames()[0]
    return game_log

# Step 2: Filter relevant columns
def filter_columns(game_log_df):
    return game_log_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GAME_DATE', 'MIN', 'PTS', 'REB', 'AST', 'PLUS_MINUS']]

# Step 3: Filter players who average at least 15 minutes per game
def filter_players_by_minutes(game_log_df):
    # Calculate total minutes and number of games per player
    player_minutes = game_log_df.groupby(['PLAYER_NAME', 'TEAM_ABBREVIATION']).agg({
        'MIN': ['sum', 'count']  # Total minutes and number of games
    }).reset_index()

    player_minutes.columns = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'TOTAL_MIN', 'GAME_COUNT']

    player_minutes['AVG_MIN'] = player_minutes['TOTAL_MIN'] / player_minutes['GAME_COUNT']

    players_filtered = player_minutes[player_minutes['AVG_MIN'] >= 15]

    # Merge filtered players back to the original game log
    filtered_game_log = game_log_df.merge(players_filtered[['PLAYER_NAME', 'TEAM_ABBREVIATION']],
                                          on=['PLAYER_NAME', 'TEAM_ABBREVIATION'])
    return filtered_game_log

# Step 4: Convert game-level data to season-level by player
def aggregate_player_stats(game_log_df):
    # Aggregating stats per player for the season
    player_aggregated = game_log_df.groupby(['PLAYER_NAME', 'TEAM_ABBREVIATION']).agg({
        'MIN': 'sum',       
        'PTS': 'mean',       
        'REB': 'mean',       
        'AST': 'mean',       
        'PLUS_MINUS': 'mean'
    }).reset_index()
    return player_aggregated

def aggregate_team_stats(player_aggregated_df):
    # Aggregating player stats into team-level season stats
    team_aggregated = player_aggregated_df.groupby('TEAM_ABBREVIATION').agg({
        'MIN': 'sum',        
        'PTS': 'mean',       
        'REB': 'mean',       
        'AST': 'mean',       
        'PLUS_MINUS': 'mean' 
    }).reset_index()
    return team_aggregated

# Step 6: Putting it all together
def create_season_team_df(season):
    game_log = get_player_game_log(season)
    # Filter relevant columns
    filtered_game_log = filter_columns(game_log)
    
    # Filter players who average at least 15 minutes per game
    filtered_game_log = filter_players_by_minutes(filtered_game_log)
    player_aggregated_stats = aggregate_player_stats(filtered_game_log)
    
    team_aggregated_stats = aggregate_team_stats(player_aggregated_stats)
    
    return team_aggregated_stats

# Example usage for season '2016-17'
season = '2016-17'
team_season_df = create_season_team_df(season)

#Merging

team_name_mapping = {
    'ATL': 'Atlanta Hawks', 'BKN': 'Brooklyn Nets', 'BOS': 'Boston Celtics', 'CHA': 'Charlotte Hornets',
    'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 
    'DET': 'Detroit Pistons', 'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies', 'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs', 'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'
}

team_season_df['Team_Full_Name'] = team_season_df['TEAM_ABBREVIATION'].map(team_name_mapping)

merged_df = pd.merge(team_season_df,df_combined_stats, left_on = 'Team_Full_Name', right_on='TEAM_NAME_base')

final_df = pd.merge(merged_df, injury_percent_df, on='TEAM_ID')

final_df.to_csv('2016-17_Complete_Data', index=False)