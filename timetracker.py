import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Time Tracker", layout="wide")

# -----------------------------
# File names
# -----------------------------
PROJECT_FILE = "projects.csv"
CLIENT_FILE = "clients.csv"
TIME_FILE = "time_log.csv"

# -----------------------------
# Create files if not exist
# -----------------------------
if not os.path.exists(PROJECT_FILE):
    pd.DataFrame(columns=["Project Name", "Client"]).to_csv(PROJECT_FILE, index=False)

if not os.path.exists(CLIENT_FILE):
    pd.DataFrame(columns=["Client"]).to_csv(CLIENT_FILE, index=False)

if not os.path.exists(TIME_FILE):
    pd.DataFrame(columns=["Date", "Project", "Client", "Task", "Start", "End", "Hours", "Notes"]).to_csv(TIME_FILE, index=False)

# -----------------------------
# Sidebar - Client Management
# -----------------------------
st.sidebar.header("Client Management")

new_client = st.sidebar.text_input("Client Name")

if st.sidebar.button("Add Client"):
    df_clients = pd.read_csv(CLIENT_FILE)
    df_clients.loc[len(df_clients)] = [new_client]
    df_clients.to_csv(CLIENT_FILE, index=False)
    st.sidebar.success("Client Added")

df_clients = pd.read_csv(CLIENT_FILE)

if not df_clients.empty:
    delete_client = st.sidebar.selectbox("Delete Client", df_clients["Client"])
    if st.sidebar.button("Delete Client"):
        df_clients = df_clients[df_clients["Client"] != delete_client]
        df_clients.to_csv(CLIENT_FILE, index=False)
        st.sidebar.warning("Client Deleted")

# -----------------------------
# Sidebar - Project Management
# -----------------------------
st.sidebar.header("Project Management")

df_clients = pd.read_csv(CLIENT_FILE)
client_list = df_clients["Client"].tolist()

new_project = st.sidebar.text_input("Project Name")
selected_client = st.sidebar.selectbox("Select Client", client_list)

if st.sidebar.button("Add Project"):
    df_projects = pd.read_csv(PROJECT_FILE)
    df_projects.loc[len(df_projects)] = [new_project, selected_client]
    df_projects.to_csv(PROJECT_FILE, index=False)
    st.sidebar.success("Project Added")

df_projects = pd.read_csv(PROJECT_FILE)

if not df_projects.empty:
    delete_project = st.sidebar.selectbox("Delete Project", df_projects["Project Name"])
    if st.sidebar.button("Delete Project"):
        df_projects = df_projects[df_projects["Project Name"] != delete_project]
        df_projects.to_csv(PROJECT_FILE, index=False)
        st.sidebar.warning("Project Deleted")

# -----------------------------
# Main Page - Time Tracker
# -----------------------------
st.title("Time Tracker")

df_projects = pd.read_csv(PROJECT_FILE)

project_list = df_projects["Project Name"].tolist()
project_client_map = dict(zip(df_projects["Project Name"], df_projects["Client"]))

task = st.selectbox("Task", ["PV Design", "Simulation", "PR Calculation", "Meeting", "Emails", "Report", "Site Visit", "Coding"])
project = st.selectbox("Project", project_list)
client = project_client_map.get(project, "")

notes = st.text_input("Notes")

col1, col2 = st.columns(2)

if col1.button("Start Timer"):
    st.session_state.start_time = datetime.now()
    st.success("Timer Started")

if col2.button("Stop Timer"):
    if "start_time" in st.session_state:
        end_time = datetime.now()
        start_time = st.session_state.start_time
        duration = (end_time - start_time).seconds / 3600

        new_entry = pd.DataFrame([[datetime.today().date(), project, client, task, start_time, end_time, duration, notes]],
                                 columns=["Date", "Project", "Client", "Task", "Start", "End", "Hours", "Notes"])

        new_entry.to_csv(TIME_FILE, mode='a', header=False, index=False)

        st.success(f"Time Logged: {round(duration,2)} hours")
    else:
        st.error("Start the timer first")

# -----------------------------
# Filters and Sorting
# -----------------------------
st.header("Time Log")

df_time = pd.read_csv(TIME_FILE)

if not df_time.empty:
    col1, col2, col3 = st.columns(3)

    filter_project = col1.selectbox("Filter by Project", ["All"] + list(df_time["Project"].unique()))
    filter_client = col2.selectbox("Filter by Client", ["All"] + list(df_time["Client"].unique()))
    sort_by = col3.selectbox("Sort By", ["Date", "Project", "Client", "Hours"])

    if filter_project != "All":
        df_time = df_time[df_time["Project"] == filter_project]

    if filter_client != "All":
        df_time = df_time[df_time["Client"] == filter_client]

    df_time = df_time.sort_values(sort_by)

    st.dataframe(df_time, use_container_width=True)

    total_hours = df_time["Hours"].sum()
    st.subheader(f"Total Hours: {round(total_hours,2)}")

    # Earnings
    st.header("Earnings Calculator")
    rate = st.number_input("Hourly Rate (£)", value=30)
    st.write(f"Total Earnings: £ {round(total_hours * rate,2)}")
else:
    st.info("No time logged yet")
