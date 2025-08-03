# Dependencies
import pandas as pd
import numpy as np
import streamlit as st
import requests
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.stats import t, percentileofscore
from nba_api.stats.endpoints import playergamelog

# Streamlit app header
st.set_page_config(page_title="NBA Stats App | Histograms & Hoops | Steven Villalon", layout="wide")
st.caption("Updated Aug 3, 2025 — v2.0")
st.title("Histograms & Hoops 🏀")
st.subheader("What are the chances your favorite NBA player will score X points?")
st.write("This question comes up often when watching games with friends. Using some basic statistical tools, we can actually answer this question...for points and a number of other basketball stats.")
st.markdown("**Uses data from the 2024-25 regular season. Next update will be made after teams play ~20 games in the 2025-26 season.**")
st.markdown("Created by: [Steven Villalon](mailto:svillal2@nd.edu)  \nSource: NBA API")
st.markdown("---")

# Load the team and player CSV files
teams_df = pd.read_csv('nba_teams.csv')
players_df = pd.read_csv('nba_players.csv')

# Define Stats
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

# Default values
default_team_player1 = 'Golden State Warriors'
default_team_player2 = 'Oklahoma City Thunder'
default_player1 = 'Stephen Curry'
default_player2 = 'Shai Gilgeous-Alexander'
season = '2024-25'

# Create two columns side by side
col1, col2 = st.columns(2)

# Label each column
with col1:
    st.header("Player 1 Stats")

with col2:
    st.header("Player 2 Stats")

# Function to grab stats for selected player and display histogram
def player_stats_block(col, col_label, team_df, player_df, stat_names):
    with col:
        team_names = team_df['full_name'].sort_values().tolist()
        
        # Choose default team and player based on column label
        default_team = default_team_player1 if col_label == "col1" else default_team_player2
        default_player = default_player1 if col_label == "col1" else default_player2

        selected_team = st.selectbox(
            "Select a Team",
            team_names,
            key=f"team_{col_label}",
            index=team_names.index(default_team)
        )

        team_id = team_df[team_df['full_name'] == selected_team]['id'].values[0]

        filtered_players = player_df[player_df['TeamID'] == team_id].sort_values('PLAYER')
        player_names = filtered_players['PLAYER'].tolist()

        # Only set the default player if present in list
        if default_player in player_names:
            default_index = player_names.index(default_player)
        else:
            default_index = 0  # fallback to first in list

        selected_player = st.selectbox(
            "Select a Player",
            player_names,
            index=default_index,
            key=f"player_{col_label}"
        )

        # Get player game logs
        player_id = filtered_players[filtered_players['PLAYER'] == selected_player]['PLAYER_ID'].values[0]
        game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
        df = game_logs.get_data_frames()[0]

        if df.empty:
            st.write("No data available for player.")
            return

        readable_names = list(stat_names.values())
        selected_readable_stat = st.selectbox("Select a Statistic", readable_names, key=f"stat_{col}")
        stat_code = {v: k for k, v in stat_names.items()}[selected_readable_stat]

        st.write(f"Showing data for {selected_player}...")
        st.markdown(f'<p style="color:orange;">Note that charts may have different scales.</p>', unsafe_allow_html=True)

        # Create interactive histogram
        fig = px.histogram(
            df,
            x=stat_code,
            nbins=10,
            title=f"{selected_player} — {stat_names[stat_code]} Distribution ({season} Regular Season)"
        )

        fig.update_layout(
            title={
                "text": f"{selected_player} — {stat_names[stat_code]} Distribution ({season} Regular Season)",
                "x": 0.5,  # Center the title
                "xanchor": "center"  # Prevent right-justification
            },
            bargap=0.1,
            xaxis_title=stat_names[stat_code],
            yaxis_title="Number of Games"
            )

        st.plotly_chart(fig, use_container_width=True)

        # Calculate summary stats
        total_games = len(df[stat_code])
        mean_stat = df[stat_code].mean()
        median_stat = df[stat_code].median()
        min_stat = df[stat_code].min()
        max_stat = df[stat_code].max()
        range_stat = max_stat - min_stat

        # Create summary stats table
        summary_data = {"Statistic": ["Games Played", "Mean", "Median", "Min", "Max", "Range"],
            stat_names[stat_code]: [
                f"{total_games}",
                f"{mean_stat:.1f}",
                f"{median_stat:.1f}",
                f"{min_stat}",
                f"{max_stat}",
                f"{range_stat}"
            ]
        }
        summary_df = pd.DataFrame(summary_data).set_index("Statistic")
        st.table(summary_df)

        # Display warning if needed
        if total_games < 30:
            st.markdown(f'<p style="color:red;">Warning: only {total_games} games in dataset.</p>', unsafe_allow_html=True)

        # Confidence Intervals
        # Calculate the Margin of Error (MOE)
        if total_games >= 20:
            alpha = 0.05
            deg_freedom = total_games - 1
            critical_value = t.ppf(1 - (alpha / 2), deg_freedom)
            std_dev = np.std(df[stat_code], ddof=1)
            moe = critical_value * (std_dev / np.sqrt(total_games))

            lower_bound = round(mean_stat - moe, 1)
            upper_bound = round(mean_stat + moe, 1)

            st.markdown(
                f"""<h5 style='color:#4da6ff; font-weight:bold;'>
                Over the next 2–3 games, {selected_player} is expected to average 
                <span style='color:white;'>between {lower_bound} and {upper_bound} {stat_names[stat_code].lower()} per game</span> with 95% statistical confidence.
                </h5>""", unsafe_allow_html=True
                )
            
        
        # Make a prediction
        # Add a number input box
        st.header("Player Prediction")
        user_input = st.number_input(
            f"Enter {stat_names[stat_code]} value to calculate a prediction:",
            value=25,
            min_value=0,
            step=1,
            key=f"prediction_input_{col_label}"  # ← unique key based on column
)

        # Calculate the quantile of the user input
        percent_below = percentileofscore(df[stat_code], user_input, kind = "strict")
        prediction = 100 - percent_below

        # Display prediction
        st.markdown(
                f"""<h5 style='color:#4da6ff; font-weight:bold;'>
                The likelihood of {selected_player} getting {user_input} {stat_names[stat_code]} or more in a game is
                <span style='color:white;'>{prediction:.1f}%.</span>
                </h5>""", unsafe_allow_html=True
                )
        

# Run function for 2 players
player_stats_block(col1, "col1", teams_df, players_df, stat_names)
player_stats_block(col2, "col2", teams_df, players_df, stat_names)


# Footer
st.markdown("***")
st.markdown(
    """
    <div style='text-align: center; padding-top: 2em;'>
        ©Copyright 2025, Steven Villalon | 
        Thanks for trying my app! 
        Check out my <a href='https://stevenvillalon.github.io/portfolio/' target='_blank' style='color:#4da6ff; font-weight:bold;'>Data Science Portfolio</a> 
        to see more of my work.
    </div>
    """,
    unsafe_allow_html=True
)
