from nba_api.stats.endpoints import LeagueGameLog
import pandas as pd

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

    # Renaming the columns for clarity
    player_minutes.columns = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'TOTAL_MIN', 'GAME_COUNT']

    # Calculate average minutes per game
    player_minutes['AVG_MIN'] = player_minutes['TOTAL_MIN'] / player_minutes['GAME_COUNT']

    # Filter players who average at least 15 minutes per game
    players_filtered = player_minutes[player_minutes['AVG_MIN'] >= 15]

    # Merge filtered players back to the original game log
    filtered_game_log = game_log_df.merge(players_filtered[['PLAYER_NAME', 'TEAM_ABBREVIATION']],
                                          on=['PLAYER_NAME', 'TEAM_ABBREVIATION'])
    return filtered_game_log

# Step 4: Convert game-level data to season-level by player
def aggregate_player_stats(game_log_df):
    # Aggregating stats per player for the season
    player_aggregated = game_log_df.groupby(['PLAYER_NAME', 'TEAM_ABBREVIATION']).agg({
        'MIN': 'sum',        # Total minutes played in the season
        'PTS': 'mean',       # Average points per game
        'REB': 'mean',       # Average rebounds per game
        'AST': 'mean',       # Average assists per game
        'PLUS_MINUS': 'mean' # Average +/- for the player
    }).reset_index()
    return player_aggregated

# Step 5: Aggregate player data to team-level for the season
def aggregate_team_stats(player_aggregated_df):
    # Aggregating player stats into team-level season stats
    team_aggregated = player_aggregated_df.groupby('TEAM_ABBREVIATION').agg({
        'MIN': 'sum',        # Total minutes for all players in the team
        'PTS': 'mean',       # Average points per player on the team
        'REB': 'mean',       # Average rebounds per player
        'AST': 'mean',       # Average assists per player
        'PLUS_MINUS': 'mean' # Average team +/- for the season
    }).reset_index()
    return team_aggregated

# Step 6: Putting it all together
def create_season_team_df(season):
    # Pull game-level data
    game_log = get_player_game_log(season)
    
    # Filter relevant columns
    filtered_game_log = filter_columns(game_log)
    
    # Filter players who average at least 15 minutes per game
    filtered_game_log = filter_players_by_minutes(filtered_game_log)
    
    # Aggregate stats by player
    player_aggregated_stats = aggregate_player_stats(filtered_game_log)
    
    # Aggregate player data into team-level stats
    team_aggregated_stats = aggregate_team_stats(player_aggregated_stats)
    
    return team_aggregated_stats

# Example usage for season '2013-14'
season = '2013-14'
team_season_df = create_season_team_df(season)

# Output: Season-level stats aggregated by team
print(team_season_df.head())

team_season_df.to_csv('2013-14_player_stats', index=False)
