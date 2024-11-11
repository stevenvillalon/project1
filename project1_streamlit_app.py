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
st.title("Histograms and Hoops")
st.subheader("How likely is your favorite player to go off for X points based on recent performance?")
st.write("This question comes up often when watching games with friends. Using some basic statistical tools, we can acutally answer these questions...for points and a number of other basketball stats.")
st.markdown('<p style="color:red;">This tool uses data from the 2023-2024 NBA regular season. I will update with data from the current season after teams have played more games.<br>Source: NBA API</p>', unsafe_allow_html=True)
st.write("App Created by Steven Villalon (svillal2@nd.edu)")

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
game_logs = playergamelog.PlayerGameLog(player_id = player_id, season = '2023', season_type_all_star = 'Regular Season')

game_logs_df = game_logs.get_data_frames()[0]

# Check if there is data available
if game_logs_df.empty:
    st.write("No data available for the selected player.")
else:
    # Step 4: User selects a statistic and displays a histogram
    statistic = st.selectbox("Select a Statistic", ['PTS', 'AST', 'OREB', 'DREB', 'REB', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS'])  # Selected Statistics

    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(game_logs_df[statistic], bins=10, edgecolor='black')
    plt.title(f"{selected_player} - {statistic} Over 2023-2024 Regular Season")
    plt.xlabel(statistic)
    plt.ylabel("Frequency")
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
        st.write(f"{total_games} games in dataset for {selected_player}.")
    st.write(f"Mean {statistic} per game = {mean_stat}")
    st.write(f"Median {statistic} per game = {median_stat}")
    st.write(f"Minimum {statistic} was {min_stat} and maximum {statistic} was {max_stat}")

    # Step 5: Add a number input box
    st.header("Make a Prediction")
    user_input = st.number_input(f"Enter {statistic} value to calculate a prediction:", min_value=0, step=1)

    # Step 6: Calculate the quantile using numpy
    less_than_input = np.sum(game_logs_df[statistic] < user_input)

    # Calculate the likelihood of scoring more than the input
    likelihood_more_than = (total_games - less_than_input) / total_games * 100

    st.write(f"The likelihood of {selected_player} getting {user_input} {statistic} or more in a game is {likelihood_more_than:.1f}%.")