import pandas as pd
import numpy as np
import streamlit as st
import requests
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelog

# Load the team and player CSV files
teams_df = pd.read_csv('nba_teams.csv')
players_df = pd.read_csv('nba_players.csv')

# Streamlit app title
st.title("Histograms and Hoops 🏀")
st.subheader("What are the chances your favorite NBA player will score X points?")
st.write("This question comes up often when watching games with friends. Using some basic statistical tools, we can actually answer this question...for points and a number of other basketball stats.")
st.markdown("<p style='color:red;'>This tool uses data from the 2023-2024 NBA regular season. I will update with data from the current season when teams have played more games.</p>", unsafe_allow_html=True)
st.markdown("App Created by [Steven Villalon](mailto:steven.villalon@gmail.com)  \nSource: NBA API")
st.markdown("---")


# Step 1: User selects an NBA team
teams_df = teams_df.sort_values('full_name')
team_names = teams_df['full_name'].tolist()
selected_team = st.selectbox("Select a Team", team_names)

# Filter players based on the selected team
team_id = teams_df[teams_df['full_name'] == selected_team]['id'].values[0]
filtered_players = players_df[players_df['TeamID'] == team_id].sort_values('PLAYER')
player_names = filtered_players['PLAYER'].tolist()

# Step 2: User selects a player
selected_player = st.selectbox("Select a Player", player_names)

# Get the player ID for the selected player
player_id = filtered_players[filtered_players['PLAYER'] == selected_player]['PLAYER_ID'].values[0]

# Step 3: Get Player Logs for Last Season
game_logs = playergamelog.PlayerGameLog(player_id=player_id, season='2023', season_type_all_star='Regular Season')
game_logs_df = game_logs.get_data_frames()[0]

# Check if there is data available
if game_logs_df.empty:
    st.write("No data available for the selected player.")
else:
    # Dictionary to map statistic codes to readable names
    stat_names = {
        'PTS': 'Points',
        'AST': 'Assists',
        'OREB': 'Offensive Rebounds',
        'DREB': 'Defensive Rebounds',
        'REB': 'Total Rebounds',
        'MIN': 'Minutes',
        'FGM': 'Field Goals Made',
        'FGA': 'Field Goals Attempted',
        'FG_PCT': 'Field Goal Percentage',
        'FG3M': '3-Point Field Goals Made',
        'FG3A': '3-Point Field Goals Attempted',
        'FG3_PCT': '3-Point Field Goal Percentage',
        'FTM': 'Free Throws Made',
        'FTA': 'Free Throws Attempted',
        'FT_PCT': 'Free Throw Percentage',
        'STL': 'Steals',
        'BLK': 'Blocks',
        'TOV': 'Turnovers',
        'PF': 'Personal Fouls',
        'PLUS_MINUS': 'Plus/Minus'
    }

    # Reverse the dictionary to map readable names back to the codes
    readable_names = list(stat_names.values())
    selected_readable_stat = st.selectbox("Select a Statistic", readable_names)
    
    # Map the user's selection back to the original statistic code
    statistic = {v: k for k, v in stat_names.items()}[selected_readable_stat]

    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(game_logs_df[statistic], bins=10, edgecolor='black')
    plt.title(f"{selected_player} - Distribution of {stat_names[statistic]} (2023-2024 Regular Season)")
    plt.xlabel(stat_names[statistic])
    plt.ylabel("Number of Games")
    st.pyplot(plt)

    # Calculate and display key statistics
    mean_stat = round(np.mean(game_logs_df[statistic]), 1)
    median_stat = round(np.median(game_logs_df[statistic]), 1)
    min_stat = np.min(game_logs_df[statistic])
    max_stat = np.max(game_logs_df[statistic])
    total_games = len(game_logs_df[statistic])

    if total_games < 40:
        st.markdown(f'<p style="color:red;">Warning: only {total_games} games in dataset.</p>', unsafe_allow_html=True)
    else:
        st.write(f"Games played = {total_games}")
    st.write(f"Mean {stat_names[statistic]} per game = {mean_stat}")
    st.write(f"Median {stat_names[statistic]} per game = {median_stat}")
    st.write(f"Minimum {stat_names[statistic]} = {min_stat}")
    st.write(f"Maximum {stat_names[statistic]} = {max_stat}")

    # Step 5: Add a number input box
    st.header("Make a Prediction")
    user_input = st.number_input(f"Enter {stat_names[statistic]} value to calculate a prediction:", min_value=0, step=1)

    # Step 6: Calculate the quantile using numpy
    less_than_input = np.sum(game_logs_df[statistic] < user_input)

    # Calculate the likelihood of scoring more than the input
    likelihood_more_than = (total_games - less_than_input) / total_games * 100

    st.write(f"The likelihood of {selected_player} getting {user_input} {stat_names[statistic]} or more in a game is {likelihood_more_than:.1f}%.")