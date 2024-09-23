import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Remove TEAM_ID, TEAM_NAME_base, TEAM_NAME_advanced
merged_df = pd.read_csv('2013-14_Complete_Data')
print(merged_df.head())








"""columns_drop = ['TEAM_ID, TEAM_NAME_base, TEAM_NAME_advanced']

merged_df = merged_df.drop(columns_drop)

print(merged_df.head())"""
