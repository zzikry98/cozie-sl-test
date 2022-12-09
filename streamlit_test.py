import requests
import json
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as mpatches
import seaborn as sns
import pytz
from pytz import timezone
import math
from textwrap import wrap
from influxdb import DataFrameClient
import streamlit as st

print("Hello World")

st.set_page_config(layout="wide")
st.title("Test title")

id_participant = "orenth45"
id_experiment = "orenth"
participant_list = ["orenth01",
                    "orenth02",
                    "orenth03",
                    "orenth04",
                    "orenth05",
                    "orenth06",
                    "orenth07",
                    "orenth08",
                    "orenth09",
                    "orenth10",
                    "orenth11",
                    "orenth12",
                    "orenth13",
                    "orenth14",
                    "orenth15",
                    "orenth16",
                    "orenth17",
                    "orenth18",
                    "orenth19",
                    "orenth20",
                    "orenth21",
                    "orenth22",
                    "orenth23",
                    "orenth24",
                    "orenth25",
                    "orenth26",
                    "orenth27",
                    "orenth28",
                    "orenth29",
                    "orenth30",
                    "orenth31",
                    "orenth32",
                    "orenth33",
                    "orenth34",
                    "orenth35",
                    "orenth36",
                    "orenth37",
                    "orenth38",
                    "orenth39",
                    "orenth40",
                    "orenth41",
                    "orenth40",
                    "orenth41",
                    "orenth42",
                    "orenth43",
                    "orenth44"]
YOUR_TIMEZONE = "Asia/Singapore"

start_of_extraction = time.time()
# Initialize InfluxDB client
host = "lonepine-64d016d6.influxcloud.net"
port = 8086
user = "Cozie-Apple-Freelancer"
password = "D4YuzwYsxVWmjHZ4Q6J0"
database = "cozie-apple"
client = DataFrameClient(host, port, user, password, database, ssl=True, verify_ssl=True)

# Query influx
query = f'SELECT * FROM "cozie-apple"."autogen"."{id_experiment}" WHERE "time">now()-10w'

print("Query:", query)

# Get result
result = client.query(query)
#print("\nResult:\n", result)
df = pd.DataFrame.from_dict(result[id_experiment])
df = df.sort_index(ascending=False)

# Convert index to local timezone
df.index = df.index.tz_convert(YOUR_TIMEZONE)

# Order timestmaps
df.sort_index(inplace=True, ascending=True)

# Parse timestamp_lambda
df["timestamp_lambda"] = pd.to_datetime(df["timestamp_lambda"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
df["timestamp_lambda"] = df["timestamp_lambda"].dt.tz_localize("UTC")
df["timestamp_lambda"] = df["timestamp_lambda"].dt.tz_convert("Asia/Singapore")

# Parse timestamp_location
df["timestamp_location"] = pd.to_datetime(df["timestamp_location"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
df["timestamp_location"] = df["timestamp_location"].dt.tz_localize("UTC")
df["timestamp_location"] = df["timestamp_location"].dt.tz_convert("Asia/Singapore")

# Parse timestamp_start
df["timestamp_start"] = pd.to_datetime(df["timestamp_start"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
df["timestamp_start"] = df["timestamp_start"].dt.tz_localize("UTC")
df["timestamp_start"] = df["timestamp_start"].dt.tz_convert("Asia/Singapore")

# Compute timestamp differences
df['timestamp'] = df.index
grouped = df[df["vote_count"].notna()].groupby(['id_participant'])

df['dT'] = (grouped['timestamp'].diff()
.astype('timedelta64[ms]')
.div(1000)
.div(60))

# Remove 'orenth' and 'admin' from 'id_participant
df = df[~((df["id_participant"]=='admin') | (df["id_participant"]=='orenth'))]

# Create backup of df
df_storage = df.copy()
df.head()

# Get fresh copy of dataframe
df = df_storage.copy()
#df = df[(df.index>date_start) | (df.id_participant==id_participant)]

# Compute Counts
df = df[df["vote_count"].notna()].groupby("id_participant")["vote_count"].count()

# --- END OF EXTRACTING DATA ---
stop_of_extraction = time.time()
print(f"Time taken to extract and format data: {stop_of_extraction - start_of_extraction} seconds")

# --- START OF BAR PLOTS ---
start_of_plotting_bar_1 = time.time()

### Plot for cohort
##df = df_storage.copy()
###date_start= datetime.datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Singapore"))-datetime.timedelta(weeks=2)
###df = df[df.index>date_start]
##
##fig, ax = plt.subplots(1,1, figsize=(30,10))
##df2 =(df[df["vote_count"].notna()]
## .groupby("id_participant")
## .resample('D')["vote_count"]
## .count()
## .unstack()
## .T)
##
##df2.plot(kind='bar', 
##       title='vote_count counts daily, individual', 
##       ylabel='Counts', 
##       xlabel='Date', 
##       figsize=(25, 7),
##       ax=ax)
##
##ax.set_xticklabels(df2.index.strftime('%d.%b').tolist()) # This line is necessary because the built in bar-plot-functionality doesn't handle datetime indexes
##ax.tick_params(axis='x', labelrotation=45) # Rotate xlabel
###ax.legend(loc=(1.05, 0.05))
##ax.legend(loc=(0, 1.2), ncol=10, title="Participant IDs")

# Plot for vote counts

# Compute bar colors
bar_color = []
labels = []
for row in df:
  if row>=100:
    bar_color.append("green")
    labels.append("complete")
  elif row>=50:
    bar_color.append("yellow")
    labels.append("JITAI phase")
  else:
    bar_color.append("blue")
    labels.append("Initial phase")

# Create custom legend
legend_elements = [mpatches.Patch(facecolor='green', edgecolor='black', label='Complete'),
                   mpatches.Patch(facecolor='yellow', edgecolor='black', label='JITAI Phase'),
                   mpatches.Patch(facecolor='blue',  edgecolor='black', label='Initial Phase')]

# Plot bars
fig, ax = plt.subplots(1,1, figsize =(20, 10))
ax = df.plot(kind='bar', 
       title='vote_count counts overall, individual', 
       ylabel='Counts', 
       xlabel='Participants', 
       color=bar_color,
       edgecolor='black',
       figsize=(25, 7))
my_legend = ax.legend(handles=legend_elements, title="Phases")
#my_legend._legend_box.align="left"

ax.tick_params(axis='x', labelrotation=90)

st.pyplot(fig)

stop_of_plotting_bar_1 = time.time()
print(f"Time taken to plot bar charts: {stop_of_plotting_bar_1 - start_of_plotting_bar_1} seconds")


print("Hello World Done")
