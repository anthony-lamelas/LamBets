from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable='2023-24')
games = gamefinder.get_data_frames()[0]


games = games[games['SEASON_ID'] == '22023']  # Filter for the 2023-24 season
games_df = games[['GAME_ID',  'MATCHUP', 'WL']]
games_df.columns = ['Game_ID', 'Matchup', 'Result']

#Extract home and away teams
def extract_teams(matchup):
    if 'vs.' in matchup:
        home_team, away_team = matchup.split(' vs. ')
    elif '@' in matchup:
        away_team, home_team = matchup.split(' @ ')
    else:
        home_team = away_team = None
    return home_team, away_team

# 7. Apply the function to the 'Matchup' column and create new columns for Home and Away teams
games_df[['Home_Team', 'Away_Team']] = games_df['Matchup'].apply(lambda x: pd.Series(extract_teams(x)))

games_df = games_df[['Game_ID', 'Home_Team', 'Away_Team', 'Result']]


print(games_df.head())

games_df.to_csv('2023-24_games', index=False)
