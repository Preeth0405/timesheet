import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("Time Tracker")

project = st.selectbox("Project", ["Project A", "Project B", "Personal"])
task = st.selectbox("Task", ["Design", "Simulation", "Meeting", "Report"])
notes = st.text_input("Notes")

if st.button("Start"):
    st.session_state.start_time = datetime.now()
    st.success("Timer Started")

if st.button("Stop"):
    end_time = datetime.now()
    start_time = st.session_state.start_time
    duration = (end_time - start_time).seconds / 3600

    data = pd.DataFrame([[datetime.today().date(), project, task, start_time, end_time, duration, notes]],
                        columns=["Date", "Project", "Task", "Start", "End", "Hours", "Notes"])

    if os.path.exists("time_log.csv"):
        data.to_csv("time_log.csv", mode='a', header=False, index=False)
    else:
        data.to_csv("time_log.csv", index=False)

    st.success(f"Time Logged: {round(duration,2)} hours")

if os.path.exists("time_log.csv"):
    df = pd.read_csv("time_log.csv")
    st.dataframe(df)
    st.write("Total Hours:", round(df["Hours"].sum(), 2))
