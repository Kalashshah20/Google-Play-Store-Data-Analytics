import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# TIME GATE - 3 PM to 5 PM IST
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)
if not (15 <= now_ist.hour < 17):
    print("This chart is only available between 3 PM - 5 PM IST.")
    exit()

data = {
    "Category":    ["GAME","SOCIAL","COMMUNICATION","TOOLS","PHOTOGRAPHY",
                    "PRODUCTIVITY","ENTERTAINMENT","EDUCATION","TRAVEL_AND_LOCAL","MUSIC_AND_AUDIO",
                    "SHOPPING","HEALTH_AND_FITNESS","FINANCE","LIFESTYLE","SPORTS"],
    "Installs":    [5000000000,3000000000,2800000000,2500000000,2000000000,
                    1800000000,1600000000,1400000000,1200000000,1100000000,
                    900000000,800000000,700000000,600000000,500000000],
    "Avg_Rating":  [4.3, 4.1, 4.2, 4.0, 4.4,
                    4.5, 3.9, 4.6, 4.2, 4.3,
                    3.8, 4.4, 3.7, 4.1, 4.2],
    "Total_Reviews":[500000,300000,280000,250000,200000,
                     180000,160000,140000,120000,110000,
                     90000,80000,70000,60000,50000],
    "Size_MB":     [80, 45, 30, 25, 60,
                    35, 50, 40, 55, 28,
                    8, 22, 12, 9, 33],
    "Last_Update": ["January 2024","January 2024","March 2024","January 2024","February 2024",
                    "January 2024","January 2024","April 2024","January 2024","January 2024",
                    "January 2024","May 2024","January 2024","June 2024","January 2024"],
}

df = pd.DataFrame(data)

# FILTER 1 - Last update must be January
df = df[df["Last_Update"].str.startswith("January")]

# FILTER 2 - Size >= 10 MB
df = df[df["Size_MB"] >= 10]

# FILTER 3 - Average rating >= 4.0
df = df[df["Avg_Rating"] >= 4.0]

# TOP 10 by installs
df = df.nlargest(10, "Installs")

# GROUPED BAR CHART
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Category"],
    y=df["Avg_Rating"],
    name="Avg Rating",
    marker_color="#2ecc71",
    yaxis="y1",
    offsetgroup="A",
))

fig.add_trace(go.Bar(
    x=df["Category"],
    y=df["Total_Reviews"],
    name="Total Reviews",
    marker_color="#3498db",
    yaxis="y2",
    offsetgroup="B",
))

fig.update_layout(
    title="Top 10 App Categories — Avg Rating vs Total Reviews<br><sup>Filter: Rating ≥ 4.0 | Size ≥ 10MB | Last Updated in January</sup>",
    xaxis=dict(title="Category", tickangle=-30),
    yaxis=dict(title="Avg Rating", range=[3.5, 5.0], showgrid=False),
    yaxis2=dict(title="Total Reviews", overlaying="y", side="right", showgrid=False),
    barmode="group",
    legend=dict(orientation="h", y=-0.3),
    plot_bgcolor="#f9f9f9",
    height=550,
)

fig.show()