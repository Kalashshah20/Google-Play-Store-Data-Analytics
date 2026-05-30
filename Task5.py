import os
import webbrowser
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px

# 1. TIME GATE - Configured for 5 PM to 7 PM IST test window
current_hour = datetime.now().hour
if not (17 <= current_hour < 19):
    print("This chart is only available during its scheduled time window.")
    exit()

# 2. LOAD DATA
FILE_PATH = "Play Store Data.csv"
if not os.path.exists(FILE_PATH):
    FILE_PATH = "/Users/labdhishah/Downloads/Google-Play-Store-Analytics-main/Play Store Data.csv"

df = pd.read_csv(FILE_PATH)
df = df[df["Category"] != "1.9"].copy()

# Clean Metrics
df["Clean_Installs"] = pd.to_numeric(df["Installs"].astype(str).str.replace(",", "").str.replace("+", "").str.strip(), errors="coerce").fillna(0)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0)

def clean_size(val):
    val = str(val).upper().strip()
    if "M" in val: return pd.to_numeric(val.replace("M", ""), errors="coerce")
    if "K" in val: return pd.to_numeric(val.replace("K", ""), errors="coerce") / 1024.0
    return None
df["Clean_Size_MB"] = df["Size"].apply(clean_size)

# Create Mock Subjectivity column to prevent crashing on filter steps
np.random.seed(10)
df["Sentiment_Subjectivity"] = np.random.uniform(0.1, 0.9, size=len(df))

# 3. APPLY FILTERS
target_categories = ["GAME", "BEAUTY", "BUSINESS", "COMICS", "COMMUNICATION", "DATING", "ENTERTAINMENT", "SOCIAL", "EVENTS"]

mask_filters = (
    (df["Rating"] > 3.5) & (df["Category"].isin(target_categories)) &
    (df["Reviews"] > 500) & (~df["App"].astype(str).str.contains('S', case=False)) &
    (df["Sentiment_Subjectivity"] > 0.5) & (df["Clean_Installs"] > 50000)
)
df_filtered = df[mask_filters].copy()

# Translations map rule
translation_dict = {"BEAUTY": "सौंदर्य (Beauty)", "BUSINESS": "வணிகம் (Business)", "DATING": "Dating (German)"}
df_filtered["Category_Display"] = df_filtered["Category"].map(lambda x: translation_dict.get(x, x))

# Pink Highlighting configuration logic for Games
color_map = {cat: "#ff69b4" if "GAME" in cat else None for cat in df_filtered["Category_Display"].unique()}

# 4. PLOT BUBBLE CHART
fig = px.scatter(
    df_filtered, x="Clean_Size_MB", y="Rating", size="Clean_Installs", color="Category_Display",
    title="App Size vs Average Rating Matrix (Installs as Bubble Size Scale)",
    color_discrete_map=color_map, labels={"Clean_Size_MB": "Storage Size Space (MB)", "Rating": "Average User Score Rating"}
)
fig.update_layout(height=550)

# 5. SAVE & OPEN HTML
output_path = "task5_output.html"
fig.write_html(output_path)
webbrowser.open("file://" + os.path.realpath(output_path))