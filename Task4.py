import os
import webbrowser
from datetime import datetime
import pandas as pd
import plotly.express as px

# 1. TIME GATE - Configured for 6 PM to 9 PM IST test window
current_hour = datetime.now().hour
if not (18 <= current_hour < 21):
    print("This chart is only available during its scheduled time window.")
    exit()

# 2. LOAD DATA
FILE_PATH = "Play Store Data.csv"
if not os.path.exists(FILE_PATH):
    FILE_PATH = "/Users/labdhishah/Downloads/Google-Play-Store-Analytics-main/Play Store Data.csv"

df = pd.read_csv(FILE_PATH)
df = df[df["Category"] != "1.9"].copy()

df["Clean_Installs"] = pd.to_numeric(df["Installs"].astype(str).str.replace(",", "").str.replace("+", "").str.strip(), errors="coerce").fillna(0)
df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0)
df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

# 3. APPLY FILTERS
mask_reviews = df["Reviews"] > 500
mask_no_xyz = ~df["App"].astype(str).str.upper().str.startswith(('X', 'Y', 'Z'))
mask_no_s = ~df["App"].astype(str).str.contains('S', case=False)
mask_cat_ebc = df["Category"].str.upper().str.startswith(('E', 'C', 'B'))

df_filtered = df[mask_reviews & mask_no_xyz & mask_no_s & mask_cat_ebc].copy()

# Add Time Period groupings
df_filtered["Year_Month"] = df_filtered["Last Updated"].dt.to_period("M")
df_ts = df_filtered.groupby(["Year_Month", "Category"])["Clean_Installs"].sum().reset_index()
df_ts["Year_Month"] = df_ts["Year_Month"].dt.to_timestamp()

# Apply required Language Translations
translation_dict = {
    "BEAUTY": "सौंदर्य (Beauty)",
    "BUSINESS": "வணிகம் (Business)",
    "DATING": "Dating (German)"
}
df_ts["Category"] = df_ts["Category"].map(lambda x: translation_dict.get(x, x))

# 4. PLOT LINE CHART
fig = px.line(df_ts, x="Year_Month", y="Clean_Installs", color="Category", title="Timeline Installation Trends over Time Columns")
fig.update_layout(xaxis_title="Timeline Interval Periods", yaxis_title="Total Installation Scale", height=550)

# 5. SAVE & OPEN HTML
output_path = "task4_output.html"
fig.write_html(output_path)
webbrowser.open("file://" + os.path.realpath(output_path))