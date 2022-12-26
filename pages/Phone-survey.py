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

df_storage = st.session_state["df_storage"]
participant_list = st.session_state["participant_list"]
plotly_labels = st.session_state["plotly_labels"]

st.title("Cozie Phone Survey")

# --- Plot 1 --- 
df = df_storage.copy()
first_question = 'This app is easy to use.'

weekly_1 = pd.DataFrame(df.groupby(by="id_participant").count()[first_question]).reset_index().rename(columns={"This app is easy to use.": "vote_count"})

fig = px.bar(weekly_1, x="id_participant", y="vote_count", category_orders=dict(id_participant=participant_list), labels=plotly_labels)
fig.update_layout(title_text="Weekly survey counts overall, individual")
st.plotly_chart(fig, use_container_width=True)

# --- Plot 2 --- 
df = df_storage.copy()
date_start= datetime.datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Singapore"))-datetime.timedelta(weeks=2)

df2 = (df[df[first_question].notna()]
 .groupby("id_participant")
 .resample('W')[first_question]
 .count()
 .unstack()
 .T)

fig = px.bar(df2, barmode='group', labels=plotly_labels)
fig.update_layout(title_text="Weekly survey counts weekly, individual", legend_title_text="Participant ID")
st.plotly_chart(fig, use_container_width=True)

# --- End of plots ---

st.caption("On the legend, double-click the desired item to view the chart for that item. Single-click to exclude item.")

