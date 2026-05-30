import os
import webbrowser
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# 1. TIME GATE - Configured for 1 PM to 2 PM IST test window
current_hour = datetime.now().hour
if not (13 <= current_hour < 14):
    print("This chart is only available during its scheduled time window.")
    exit()

# 2. LOAD & CLEAN DATA
FILE_PATH = "Play Store Data.csv"
if not os.path.exists(FILE_PATH):
    FILE_PATH = "/Users/labdhishah/Downloads/Google-Play-Store-Analytics-main/Play Store Data.csv"

df = pd.read_csv(FILE_PATH)
df = df[df["Category"] != "1.9"].copy()

df["Clean_Installs"] = pd.to_numeric(df["Installs"].astype(str).str.replace(",", "").str.replace("+", "").str.strip(), errors="coerce").fillna(0)
df["Clean_Price"] = pd.to_numeric(df["Price"].astype(str).str.replace("$", "", regex=False).str.strip(), errors="coerce").fillna(0.0)
df["Revenue"] = df["Clean_Price"] * df["Clean_Installs"]

def clean_size(val):
    val = str(val).upper().strip()
    if "M" in val: return pd.to_numeric(val.replace("M", ""), errors="coerce")
    if "K" in val: return pd.to_numeric(val.replace("K", ""), errors="coerce") / 1024.0
    return None
df["Clean_Size_MB"] = df["Size"].apply(clean_size)
df["Clean_Android_Ver"] = df["Android Ver"].astype(str).str.extract(r"^(\d+\.\d+)").astype(float)

# 3. APPLY FILTER CODES
mask_installs = df["Clean_Installs"] >= 10000
mask_revenue = (df["Revenue"] >= 10000) | (df["Type"] == "Free") # Protects Free tiers from disappearing
mask_android = df["Clean_Android_Ver"] > 4.0
mask_size = df["Clean_Size_MB"] > 15.0
mask_content = df["Content Rating"].str.strip() == "Everyone"
mask_name_len = df["App"].astype(str).str.len() <= 30

df_filtered = df[mask_installs & mask_revenue & mask_android & mask_size & mask_content & mask_name_len].copy()

# Pull top 3 surviving categories
top_3 = df_filtered["Category"].value_counts().nlargest(3).index.tolist()
df_final = df_filtered[df_filtered["Category"].isin(top_3)]

# Aggregate averages
agg = df_final.groupby(["Category", "Type"])[["Clean_Installs", "Revenue"]].mean().reset_index()
agg["Label"] = agg["Category"] + " (" + agg["Type"] + ")"

# 4. PLOT CHART
fig = go.Figure()
fig.add_trace(go.Bar(x=agg["Label"], y=agg["Clean_Installs"], name="Avg Installs", yaxis="y1", marker_color="#2980b9"))
fig.add_trace(go.Bar(x=agg["Label"], y=agg["Revenue"], name="Avg Revenue ($)", yaxis="y2", marker_color="#27ae60"))

fig.update_layout(
    title="Free vs Paid App Metrics (Top 3 Categories)",
    barmode="group",
    xaxis=dict(title="Category and Pricing Variant Structure"),
    yaxis=dict(title="Average Installations Metric", side="left"),
    yaxis2=dict(title="Average Revenue Metric ($)", side="right", overlaying="y", type="linear"),
    height=550
)

# 5. SAVE & OPEN HTML
output_path = "task3_output.html"
fig.write_html(output_path)
webbrowser.open("file://" + os.path.realpath(output_path))