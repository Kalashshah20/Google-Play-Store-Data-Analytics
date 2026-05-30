import os
import webbrowser
from datetime import datetime
import pandas as pd
import plotly.express as px

# 1. TIME GATE - Configured for 4 PM to 6 PM IST test window
current_hour = datetime.now().hour
if not (16 <= current_hour < 18):
    print("This chart is only available during its scheduled time window.")
    exit()

# 2. LOAD DATA
FILE_PATH = "Play Store Data.csv"
if not os.path.exists(FILE_PATH):
    FILE_PATH = "/Users/labdhishah/Downloads/Google-Play-Store-Analytics-main/Play Store Data.csv"

df = pd.read_csv(FILE_PATH)
df = df[df["Category"] != "1.9"].copy()

df["Clean_Installs"] = pd.to_numeric(df["Installs"].astype(str).str.replace(",", "").str.replace("+", "").str.strip(), errors="coerce").fillna(0)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0)
df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

def clean_size(val):
    val = str(val).upper().strip()
    if "M" in val: return pd.to_numeric(val.replace("M", ""), errors="coerce")
    if "K" in val: return pd.to_numeric(val.replace("K", ""), errors="coerce") / 1024.0
    return None
df["Clean_Size_MB"] = df["Size"].apply(clean_size)

# 3. APPLY FILTERS
mask_rating = df["Rating"] >= 4.2
mask_no_digits = ~df["App"].astype(str).str.contains(r'\d', regex=True)
mask_prefix_tp = df["Category"].str.upper().str.startswith(('T', 'P'))
mask_reviews = df["Reviews"] > 1000
mask_size_bounds = (df["Clean_Size_MB"] >= 20.0) & (df["Clean_Size_MB"] <= 80.0)

df_filtered = df[mask_rating & mask_no_digits & mask_prefix_tp & mask_reviews & mask_size_bounds].copy()

df_filtered["Year_Month"] = df_filtered["Last Updated"].dt.to_period("M")
df_area = df_filtered.groupby(["Year_Month", "Category"])["Clean_Installs"].sum().reset_index()
df_area["Year_Month"] = df_area["Year_Month"].dt.to_timestamp()

# Legend International translations map
legend_translations = {
    "TRAVEL_AND_LOCAL": "Voyages et infos locales (French)",
    "PRODUCTIVITY": "Productividad (Spanish)",
    "PHOTOGRAPHY": "写真 (Photography)"
}
df_area["Category_Legend"] = df_area["Category"].map(lambda x: legend_translations.get(x, x))

# 4. PLOT STACKED AREA CHART
fig = px.area(df_area, x="Year_Month", y="Clean_Installs", color="Category_Legend", title="Cumulative Volume Distribution Profile Bands")
fig.update_layout(xaxis_title="Timeline Track Axis", yaxis_title="Cumulative Volumetric Growth Units", height=550)

# 5. SAVE & OPEN HTML
output_path = "task6_output.html"
fig.write_html(output_path)
webbrowser.open("file://" + os.path.realpath(output_path))