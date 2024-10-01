import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Remove TEAM_ID, TEAM_NAME_base, TEAM_NAME_advanced
merged_df = pd.read_csv('C:/Users/antho/OneDrive/Documents/Coding/LamBets/Data/Merged Data/StudentPerformanceFactors.csv')
print(merged_df.head())


columns_drop = ['TEAM_ID, TEAM_NAME_base, TEAM_NAME_advanced']

merged_df = merged_df.drop(columns_drop)

print(merged_df.head())

# StandardScaler to scale and transform merged data
numeric_columns = merged_df.select_dtypes(include=['float64', 'int64']).columns

scaler = StandardScaler()
scaled_data = scaler.fit_transform(merged_df[numeric_columns])

print(scaled_data.head())


# OneHotEncoder used to Encode TEAM_ABBREVIATION

enc = OneHotEncoder(handle_unknown = 'ignore', sparse = False)

team_abr_encoded = enc.fit_transform(merged_df[["TEAM_ABBREVIATION"]])

team_abbr_encoded_df = pd.DataFrame(team_abr_encoded, 
                    columns=enc.get_feature_names_out(["TEAM_ABBREVIATION"]))

merged_df = pd.concat([merged_df.reset_index(drop=True), team_abbr_encoded_df], axis=1)

# OneHotEncoder used to Encode home and away team

train_df = pd.read_csv('2013-14_games')
train_df['Result'] = train_df['Result'].replace({'W' : 1, 'L' : 0})


home_away_encoded = enc.fit_transform(train_df[['Home_Team', 'Away_Team']])

home_away_enc_df = pd.DataFrame(home_away_encoded, columns = 
                        enc.get_feature_names_out(['Home_Team', 'Away_Team']))

train_df = pd.concat([train_df.reset_index(drop=True), home_away_enc_df], axis=1)


