import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import LeagueGameLog

# Step 1: Fetch Player Stats
def get_player_stats(season):
    # Fetch player stats from the API
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star='Regular Season',
        per_mode_detailed='PerGame'
    ).get_data_frames()[0]

    print(player_stats.columns)  # Check available columns

    # Filter for relevant columns (PLAYER_NAME, TEAM_ID, PLUS_MINUS_RANK)
    df_players = player_stats[['PLAYER_NAME', 'TEAM_ID', 'PLUS_MINUS']]  # Adjust based on actual columns

    return df_players

# Step 2: Merge Team and Player Data
def merge_team_player_data(team_df, player_df):
    # Merge player data with team data on TEAM_ID
    merged_df = pd.merge(team_df, player_df, on='TEAM_ID', how='inner')

    return merged_df

# Step 2: Get Top 2 PLUS_MINUS_RANK Players for Each Team
def get_top_2_per_players(merged_df):
    # Group by team and get top 2 players by PLUS_MINUS_RANK for each team
    top_2_per_players = merged_df.groupby('TEAM_ID').apply(lambda x: x.nlargest(2, 'PLUS_MINUS_RANK')).reset_index(drop=True)
    
    return top_2_per_players

# Step 4: Calculate Major Injury Percentage
def check_major_injuries(team_season_df, top_2_per_players, season):
    # Fetch game logs for the season
    game_log = LeagueGameLog(season=season, player_or_team_abbreviation='P').get_data_frames()[0]
    
    # Initialize a column to store injury percentages
    team_season_df['Major_Injury_Percent'] = 0
    
    # Loop through each team
    for team in team_season_df['TEAM_ID']:
        # Get top 2 players by PLUS_MINUS_RANK for the team
        top_2_players = top_2_per_players[top_2_per_players['TEAM_ID'] == team]['PLAYER_NAME']
        
        # Filter game log for this team's games
        team_games = game_log[game_log['TEAM_ID'] == team]

        # Initialize a count of games where all top 2 players played
        games_with_all_top_2 = 0
        
        # Loop through each game and check if all top 2 players played
        for game_id in team_games['GAME_ID'].unique():
            game = team_games[team_games['GAME_ID'] == game_id]
            players_in_game = game['PLAYER_NAME'].tolist()
            
            # Check if all top 2 players are in the game
            if all(player in players_in_game for player in top_2_players):
                games_with_all_top_2 += 1
        
        # Calculate the percentage of games where not all top 2 players played
        total_games = len(team_games['GAME_ID'].unique())
        injury_percent = ((total_games - games_with_all_top_2) / total_games) * 100
        
        # Update the DataFrame
        team_season_df.loc[team_season_df['TEAM_ID'] == team, 'Major_Injury_Percent'] = injury_percent
    
    return team_season_df

# Main Workflow
season = '2013-14'

# Fetch team stats
team_df = leaguedashteamstats.LeagueDashTeamStats(season=season).get_data_frames()[0]

# Fetch player stats
player_df = get_player_stats(season)

# Merge the team and player data
merged_df = merge_team_player_data(team_df, player_df)

# Get top 2 players per team by PLUS_MINUS_RANK
top_2_per_players = get_top_2_per_players(merged_df)

# Assuming `team_season_df` contains the relevant team data you are using, 
# you can then calculate the injury percentage:
team_season_df = team_df.copy()  # Create a copy if needed
team_season_df = check_major_injuries(team_season_df, top_2_per_players, season)

injury_percent_df = team_season_df[['TEAM_ID', "Major_Injury_Percent"]]


print(injury_percent_df)


