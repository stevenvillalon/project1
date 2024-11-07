import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Sample Data (replace this with your actual DataFrame)
data = {
    'Player name': ['LeBron James', 'Anthony Davis', 'Stephen Curry', 'Klay Thompson'],
    'Team': ['Los Angeles Lakers', 'Los Angeles Lakers', 'Golden State Warriors', 'Golden State Warriors'],
    'Game date': ['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02'],
    'Points': [30, 20, 35, 25],
    'Rebounds': [8, 10, 5, 6],
    'Assists': [7, 5, 9, 4],
    'Steals': [1, 0, 2, 1],
    'Blocks': [1, 2, 0, 1]
}

# Load the DataFrame
df = pd.DataFrame(data)

# Streamlit App
st.title("NBA Player Performance Analysis")

# Step 1: Select Team
team = st.selectbox("Select Team:", df['Team'].unique())

# Step 2: Select Player (filtered by the selected team)
filtered_players = df[df['Team'] == team]['Player name'].unique()
player = st.selectbox("Select Player:", filtered_players)

# Step 3: Select Metric
metric = st.selectbox("Select Metric:", ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks'])

# Filter data for the selected player
player_data = df[df['Player name'] == player]
metric_data = player_data[metric]

# Display Histogram
st.subheader(f"Histogram of {metric} for {player}")
fig, ax = plt.subplots()
ax.hist(metric_data, bins=10, color='skyblue', edgecolor='black')
ax.set_xlabel(metric)
ax.set_ylabel("Frequency")
st.pyplot(fig)

# Slider for cumulative density prediction
threshold = st.slider(f"Select threshold for cumulative density of {metric}", int(metric_data.min()), int(metric_data.max()))
mean, std_dev = metric_data.mean(), metric_data.std()
cumulative_prob = norm.cdf(threshold, mean, std_dev)

st.subheader(f"Cumulative Probability of Scoring {threshold} or less in {metric}")
st.write(f"The probability is approximately: {cumulative_prob:.2%}")
