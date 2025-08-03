import pandas as pd
import numpy as np
from scipy.stats import t, percentileofscore
import streamlit as st
import requests
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelog

# Streamlit app header
st.set_page_config(page_title="NBA Stats App | Histograms and Hoops | Steven Villalon", layout="wide")
st.caption("Updated Aug 2, 2025 — v1.1")
st.title("Histograms and Hoops 🏀")
st.subheader("What are the chances your favorite NBA player will score X points?")
st.write("This question comes up often when watching games with friends. Using some basic statistical tools, we can actually answer this question...for points and a number of other basketball stats.")
st.markdown("<p style='color:yellow;'>Uses data from the 2024-25 regular season. Next update after teams play ~20 games in the 2025-26 season.</p>", unsafe_allow_html=True)
st.markdown("Created by: [Steven Villalon](mailto:svillal2@nd.edu)  \nSource: NBA API")
st.markdown("---")

# Step 0: Load the team and player CSV files
teams_df = pd.read_csv('nba_teams.csv')
players_df = pd.read_csv('nba_players.csv')


# Step 1: Select a team
teams_df = teams_df.sort_values('full_name')
team_names = teams_df['full_name'].tolist()
selected_team = st.selectbox("Select a Team", team_names, index=team_names.index("Los Angeles Lakers"))

# Filter players based on the selected team
team_id = teams_df[teams_df['full_name'] == selected_team]['id'].values[0]
filtered_players = players_df[players_df['TeamID'] == team_id].sort_values('PLAYER')
player_names = filtered_players['PLAYER'].tolist()


# Step 2: Select a player
default_player = player_names[0] if "LeBron James" not in player_names else "LeBron James"
selected_player = st.selectbox("Select a Player", player_names, index=player_names.index(default_player))

# Get the player ID for the selected player
player_id = filtered_players[filtered_players['PLAYER'] == selected_player]['PLAYER_ID'].values[0]


# Step 3: Get player logs for selected player
game_logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25', season_type_all_star='Regular Season')
game_logs_df = game_logs.get_data_frames()[0]


# Step 4: Select a KPI of interest
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

    
    # Step 5: Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(game_logs_df[statistic], bins=10, edgecolor='black')
    plt.title(f"{selected_player} - Distribution of {stat_names[statistic]} (2024-2025 Regular Season)")
    plt.xlabel(stat_names[statistic])
    plt.ylabel("Number of Games")
    st.pyplot(plt)

   
    # Step 6: Calculate and display key statistics
    mean_stat = round(np.mean(game_logs_df[statistic]), 1)
    median_stat = round(np.median(game_logs_df[statistic]), 1)
    min_stat = np.min(game_logs_df[statistic])
    max_stat = np.max(game_logs_df[statistic])
    total_games = len(game_logs_df[statistic])

    if total_games < 30:
        st.markdown(f'<p style="color:red;">Warning: only {total_games} games in dataset.</p>', unsafe_allow_html=True)
    else:
        st.write(f"Games played = {total_games}")
    st.write(f"Mean {stat_names[statistic]} per game = {mean_stat}")
    st.write(f"Median {stat_names[statistic]} per game = {median_stat}")
    st.write(f"Minimum {stat_names[statistic]} = {min_stat}")
    st.write(f"Maximum {stat_names[statistic]} = {max_stat}")

    
    # Step 7: Add Confidence Intervals
    # Calculate the Margin of Error (MOE)
    if total_games >= 20:
        alpha = 0.05
        deg_freedom = total_games - 1
        critical_value = t.ppf(1 - (alpha / 2), deg_freedom)
        std_dev = np.std(game_logs_df[statistic], ddof=1)
        moe = critical_value * (std_dev / np.sqrt(total_games))
        
        lower_bound = round(mean_stat - moe, 1)
        upper_bound = round(mean_stat + moe, 1)

        st.markdown(f"**<h5 style='color:green'>In the short-term (2-3 games), we are 95% confident that {selected_player} will average between {lower_bound} and {upper_bound} {stat_names[statistic]} per game.</h5>**", unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:red;">Not enough games played to calculate a valid prediction interval.</p>', unsafe_allow_html=True)


    # Step 8: Make a prediction
    # Add a number input box
    st.header("Make a Prediction")
    user_input = st.number_input(f"Enter {stat_names[statistic]} value to calculate a prediction:", value = 25, min_value=0, step=1)


    # Calculate the quantile of the user input
    percent_below = percentileofscore(game_logs_df[statistic], user_input, kind = "strict")
    prediction = 100 - percent_below

    st.markdown(f"**<h5 style='color:green'>The likelihood of {selected_player} getting {user_input} {stat_names[statistic]} or more in a game is {prediction:.1f}%.</h5>**", unsafe_allow_html=True)
    

st.markdown("***")
st.markdown(
        "©Copyright 2025, Steven Villalon | Thanks for trying my app! Check out my [Data Science Portfolio](https://stevenvillalon.github.io/portfolio/) to see more of my work.")
