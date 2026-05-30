import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import numpy as np

# TIME GATE
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)

if not (18 <= now_ist.hour < 20):
    print("This chart is only available between 6 PM - 8 PM IST.")
    exit()

# DATA - more countries so map is populated
data = {
    "Category": [
        "VIDEO_PLAYERS","VIDEO_PLAYERS","VIDEO_PLAYERS","VIDEO_PLAYERS","VIDEO_PLAYERS",
        "TOOLS","TOOLS","TOOLS","TOOLS","TOOLS","TOOLS",
        "MUSIC_AND_AUDIO","MUSIC_AND_AUDIO","MUSIC_AND_AUDIO","MUSIC_AND_AUDIO",
        "TRAVEL_AND_LOCAL","TRAVEL_AND_LOCAL","TRAVEL_AND_LOCAL","TRAVEL_AND_LOCAL",
        "PHOTOGRAPHY","PHOTOGRAPHY","PHOTOGRAPHY","PHOTOGRAPHY",
        # Excluded (A/C/G/S) - will be filtered
        "SOCIAL","COMMUNICATION","GAME","SHOPPING",
    ],
    "Country": [
        "United States","India","France","Brazil","Germany",
        "China","Sweden","United States","United Kingdom","Czech Republic","Russia",
        "Sweden","Germany","United States","India",
        "United States","India","Netherlands","Australia",
        "United States","South Korea","Russia","Japan",
        # Excluded
        "United States","India","Finland","United States",
    ],
    "Installs": [
        5000000000, 500000000, 550000000, 300000000, 200000000,
        2000000000, 500000000, 600000000, 50000000, 100000000, 80000000,
        500000000, 500000000, 100000000, 200000000,
        1000000000, 100000000, 50000000, 30000000,
        1000000000, 200000000, 100000000, 150000000,
        # Excluded
        1000000000, 1000000000, 500000000, 500000000,
    ]
}

df = pd.DataFrame(data)

# FILTER 1 - Remove categories starting with A, C, G, S
df = df[~df["Category"].str.startswith(("A", "C", "G", "S"))]

# FILTER 2 - Top 5 categories
top5 = df.groupby("Category")["Installs"].sum().nlargest(5).index.tolist()
df = df[df["Category"].isin(top5)]

# AGGREGATE by country
country_df = df.groupby("Country")["Installs"].sum().reset_index()
country_df["Log_Installs"] = np.log10(country_df["Installs"])
country_df["Exceeds_1M"] = country_df["Installs"] > 1_000_000
country_df["Label"] = country_df["Installs"].apply(
    lambda x: f"{x/1e9:.1f}B" if x >= 1e9 else f"{x/1e6:.0f}M"
)

# CHOROPLETH
fig = px.choropleth(
    country_df,
    locations="Country",
    locationmode="country names",
    color="Log_Installs",
    hover_name="Country",
    hover_data={"Label": True, "Exceeds_1M": True, "Log_Installs": False},
    color_continuous_scale="Blues",
    title="Global App Installs by Category (Top 5) | Gold border = Exceeds 1M",
)

# Highlight countries exceeding 1M with gold border
over1m = country_df[country_df["Exceeds_1M"]]
fig.add_trace(
    __import__("plotly.graph_objects", fromlist=["Choropleth"]).Choropleth(
        locations=over1m["Country"],
        locationmode="country names",
        z=[1] * len(over1m),
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        marker_line_color="gold",
        marker_line_width=2,
        hoverinfo="skip",
        name="Exceeds 1M",
    )
)

fig.update_coloraxes(
    colorbar_tickvals=[6, 7, 8, 9, 10],
    colorbar_ticktext=["1M", "10M", "100M", "1B", "10B"],
    colorbar_title="Installs"
)

fig.update_layout(height=600)
fig.show()