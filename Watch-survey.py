import requests
import json
import pandas as pd
import numpy as np
import time
import datetime
import pytz
from pytz import timezone
import math
from textwrap import wrap
from influxdb import DataFrameClient
import streamlit as st
import plotly.express as px
import plotly          
import plotly.graph_objects as go

print("Hello World")

st.set_page_config(page_title="Watch survey", layout="wide")
st.title("Cozie Watch Survey")

with st.spinner("Loading data... Please wait for this page to fully load before viewing other pages"):
  start_of_extraction = time.time()

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

  st.session_state["participant_list"] = participant_list


  ### --- New extraction code ---
  s3_pickle_path = "https://cozie-dashboard.s3.ap-southeast-1.amazonaws.com/cozie_orenth_pickle.zip"
  response = requests.get(s3_pickle_path)

  open("s3_pickle.zip", "wb").write(response.content)
  df = pd.read_pickle("./s3_pickle.zip")
  ### --- End of new extraction code ---

  df = pd.DataFrame.from_dict(df)
  df = df.sort_index(ascending=False)

  # Convert index to local timezone
  df.index = df.index.tz_convert(YOUR_TIMEZONE)

  # Order timestmaps
  df.sort_index(inplace=True, ascending=True)

  # Parse timestamp_lambda
  df["timestamp_lambda"] = pd.to_datetime(df["timestamp_lambda"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
  ##df["timestamp_lambda"] = df["timestamp_lambda"].dt.tz_localize("UTC")
  df["timestamp_lambda"] = df["timestamp_lambda"].dt.tz_convert("Asia/Singapore")

  # Parse timestamp_location
  df["timestamp_location"] = pd.to_datetime(df["timestamp_location"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
  ##df["timestamp_location"] = df["timestamp_location"].dt.tz_localize("UTC")
  df["timestamp_location"] = df["timestamp_location"].dt.tz_convert("Asia/Singapore")

  # Parse timestamp_start
  df["timestamp_start"] = pd.to_datetime(df["timestamp_start"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
  ##df["timestamp_start"] = df["timestamp_start"].dt.tz_localize("UTC")
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

  st.session_state["df_storage"] = df_storage

  # Get fresh copy of dataframe
  df = df_storage.copy()
  #df = df[(df.index>date_start) | (df.id_participant==id_participant)]

  # Compute Counts
  df = df[df["vote_count"].notna()].groupby("id_participant")["vote_count"].count()

  # --- END OF EXTRACTING DATA ---
  stop_of_extraction = time.time()
  print(f"Time taken to extract and format data: {stop_of_extraction - start_of_extraction} seconds")
  print("Hello World Done")

  df.to_csv("df.csv")

  # --- PLOTLY TEST ---

  # --- BAR CHART ---

  plotly_labels = {"vote_count": "Counts", "id_participant": "Participant ID", "date_time": "Date & Time", "value": "Counts", "index": "Weeks"}
  st.session_state["plotly_labels"] = plotly_labels

  df_plotly = df.copy()
  df_plotly=df_plotly.reset_index()

  df_plotly['phase'] = "Initial Phase"
  for i in df_plotly.index:
      if df_plotly.at[i, "vote_count"] >= 100:
          df_plotly.at[i, "phase"] = "Complete"
      elif df_plotly.at[i, "vote_count"] >= 50:
          df_plotly.at[i, "phase"] = "JITAI Phase"

  fig = px.bar(df_plotly, y="vote_count", x="id_participant", color="phase", category_orders=dict(id_participant=participant_list),\
    color_discrete_map={"Complete": "green", "JITAI Phase": "yellow", "Initial Phase": "blue"}, labels=plotly_labels)

  fig.update_layout(title_text="vote_count counts overall, individual", legend_title_text="Phases")

  st.plotly_chart(fig, use_container_width=True)

  # --- END OF BAR CHART ---

  # --- LINE CHART ---
  
  df = df_storage.copy()
  #df = df[(df.index>date_start) & df.vote_count.notna()]
  df = df[df.vote_count.notna()]
  df.id_participant.unique()
  df['vote_count_count'] = (df
   .groupby('id_participant')["vote_count"]
   .cumcount()
  )

  df_line_chart = df.copy().reset_index().rename(columns={"index": "date_time"})

  grey_bg = [{'type': 'rect',
    'xref': 'paper',
    'yref': 'y',
    'x0': 0,
    'y0': 100,
    'x1': 1,
    'y1': 190,
    'fillcolor': '#b5b5b5',
    'opacity': 0.5,
    'layer': 'below',
    'line_width': 0}]

  fig = px.line(df_line_chart, x="date_time", y="vote_count", color="id_participant", labels=plotly_labels)
  fig.update_layout(title_text="vote_count cumcounts, individual", legend_title_text="Experiment ID", shapes=grey_bg)
  st.plotly_chart(fig, use_container_width=True)
  
  # --- END OF LINE CHART ---

  st.caption("On the legend, double-click the desired item to view the chart for that item. Single-click to exclude item.")

print("Hello World Done")
