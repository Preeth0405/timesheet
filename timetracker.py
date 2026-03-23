import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="Time Tracker", layout="wide")

PROJECT_FILE = "projects.csv"
CLIENT_FILE = "clients.csv"
TIME_FILE = "time_log.csv"

columns_order = ["Date", "Project", "Client", "Task", "Start", "End", "Hours", "Notes"]

# Create files if not exist
if not os.path.exists(PROJECT_FILE):
    pd.DataFrame(columns=["Project Name", "Client"]).to_csv(PROJECT_FILE, index=False)

if not os.path.exists(CLIENT_FILE):
    pd.DataFrame(columns=["Client"]).to_csv(CLIENT_FILE, index=False)

if not os.path.exists(TIME_FILE):
    pd.DataFrame(columns=columns_order).to_csv(TIME_FILE, index=False)

# Load data
df_projects = pd.read_csv(PROJECT_FILE)
df_clients = pd.read_csv(CLIENT_FILE)
df_time = pd.read_csv(TIME_FILE)

# Ensure correct columns
for col in columns_order:
    if col not in df_time.columns:
        df_time[col] = ""

df_time = df_time[columns_order]
df_time.to_csv(TIME_FILE, index=False)

# ---------------- Sidebar ----------------
st.sidebar.header("Client Management")
new_client = st.sidebar.text_input("Client Name")
if st.sidebar.button("Add Client"):
    if new_client != "":
        df_clients.loc[len(df_clients)] = [new_client]
        df_clients.to_csv(CLIENT_FILE, index=False)
        st.sidebar.success("Client Added")

if not df_clients.empty:
    delete_client = st.sidebar.selectbox("Delete Client", df_clients["Client"])
    if st.sidebar.button("Delete Client"):
        df_clients = df_clients[df_clients["Client"] != delete_client]
        df_clients.to_csv(CLIENT_FILE, index=False)
        st.sidebar.warning("Client Deleted")

st.sidebar.header("Project Management")
client_list = df_clients["Client"].tolist() if not df_clients.empty else []
new_project = st.sidebar.text_input("Project Name")
selected_client = st.sidebar.selectbox("Select Client", client_list) if client_list else ""

if st.sidebar.button("Add Project"):
    if new_project != "" and selected_client != "":
        df_projects.loc[len(df_projects)] = [new_project, selected_client]
        df_projects.to_csv(PROJECT_FILE, index=False)
        st.sidebar.success("Project Added")

if not df_projects.empty:
    delete_project = st.sidebar.selectbox("Delete Project", df_projects["Project Name"])
    if st.sidebar.button("Delete Project"):
        df_projects = df_projects[df_projects["Project Name"] != delete_project]
        df_projects.to_csv(PROJECT_FILE, index=False)
        st.sidebar.warning("Project Deleted")

# ---------------- Main ----------------
st.title("Time Tracker")

df_projects = pd.read_csv(PROJECT_FILE)
project_list = df_projects["Project Name"].tolist() if not df_projects.empty else []
project_client_map = dict(zip(df_projects["Project Name"], df_projects["Client"]))

task = st.selectbox("Task", ["PV Design", "Simulation", "PR Calculation", "Meeting", "Emails", "Report", "Site Visit", "Coding"])
project = st.selectbox("Project", project_list) if project_list else ""
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
        duration = (end_time - start_time).total_seconds() / 3600

        new_entry = pd.DataFrame([[datetime.today().date(), project, client, task, start_time, end_time, duration, notes]],
                                 columns=columns_order)

        new_entry = new_entry[columns_order]
        new_entry.to_csv(TIME_FILE, mode='a', header=False, index=False)
        st.success(f"Time Logged: {round(duration,2)} hours")
    else:
        st.error("Start the timer first")

# ---------------- Time Log ----------------
st.header("Time Log")

df_time = pd.read_csv(TIME_FILE)
df_time = df_time[columns_order]

if not df_time.empty:
    col1, col2, col3 = st.columns(3)
    project_options = ["All"] + list(df_time["Project"].dropna().unique())
    client_options = ["All"] + list(df_time["Client"].dropna().unique())

    filter_project = col1.selectbox("Filter by Project", project_options)
    filter_client = col2.selectbox("Filter by Client", client_options)
    sort_by = col3.selectbox("Sort By", ["Date", "Project", "Client", "Hours"])

    if filter_project != "All":
        df_time = df_time[df_time["Project"] == filter_project]
    if filter_client != "All":
        df_time = df_time[df_time["Client"] == filter_client]

    df_time = df_time.sort_values(sort_by)
    st.dataframe(df_time, use_container_width=True, height=400)

    total_hours = pd.to_numeric(df_time["Hours"], errors="coerce").sum()
    st.subheader(f"Total Hours: {round(total_hours,2)}")

    rate = st.number_input("Hourly Rate (£)", value=30)
    st.write(f"Total Earnings: £ {round(total_hours * rate,2)}")

# ---------------- Edit/Delete ----------------
st.header("Edit / Delete Entry")

df_time = pd.read_csv(TIME_FILE)
df_time["Row ID"] = df_time.index

if not df_time.empty:
    selected_row = st.selectbox("Select Entry", df_time["Row ID"])
    row_data = df_time[df_time["Row ID"] == selected_row].iloc[0]

    edit_date = st.date_input("Date", pd.to_datetime(row_data["Date"]))
    edit_project = st.text_input("Project", row_data["Project"])
    edit_client = st.text_input("Client", row_data["Client"])
    edit_task = st.text_input("Task", row_data["Task"])
    edit_start = st.text_input("Start Time (YYYY-MM-DD HH:MM:SS)", row_data["Start"])
    edit_end = st.text_input("End Time (YYYY-MM-DD HH:MM:SS)", row_data["End"])
    edit_notes = st.text_input("Notes", row_data["Notes"])

    try:
        start_dt = pd.to_datetime(edit_start)
        end_dt = pd.to_datetime(edit_end)
        edit_hours = (end_dt - start_dt).total_seconds() / 3600
        st.write(f"Calculated Hours: {round(edit_hours,2)}")
    except:
        edit_hours = 0
        st.warning("Check time format")

    col1, col2 = st.columns(2)

    if col1.button("Update Entry"):
        df_time.loc[selected_row, "Date"] = edit_date
        df_time.loc[selected_row, "Project"] = edit_project
        df_time.loc[selected_row, "Client"] = edit_client
        df_time.loc[selected_row, "Task"] = edit_task
        df_time.loc[selected_row, "Start"] = edit_start
        df_time.loc[selected_row, "End"] = edit_end
        df_time.loc[selected_row, "Hours"] = edit_hours
        df_time.loc[selected_row, "Notes"] = edit_notes

        df_time.drop(columns=["Row ID"], inplace=True)
        df_time.to_csv(TIME_FILE, index=False)
        st.success("Entry Updated")

    if col2.button("Delete Entry"):
        df_time = df_time[df_time["Row ID"] != selected_row]
        df_time.drop(columns=["Row ID"], inplace=True)
        df_time.to_csv(TIME_FILE, index=False)
        st.warning("Entry Deleted")

# ---------------- Dashboard ----------------
st.header("Dashboard")

df_time = pd.read_csv(TIME_FILE)

if not df_time.empty:
    df_time["Date"] = pd.to_datetime(df_time["Date"], errors='coerce')
    df_time["Hours"] = pd.to_numeric(df_time["Hours"], errors="coerce")

    daily_hours = df_time.groupby("Date")["Hours"].sum().reset_index()
    fig1 = px.bar(daily_hours, x="Date", y="Hours", title="Daily Hours")
    st.plotly_chart(fig1, use_container_width=True)

    project_hours = df_time.groupby("Project")["Hours"].sum().reset_index()
    fig2 = px.pie(project_hours, names="Project", values="Hours", title="Hours by Project")
    st.plotly_chart(fig2, use_container_width=True)

    client_hours = df_time.groupby("Client")["Hours"].sum().reset_index()
    fig3 = px.pie(client_hours, names="Client", values="Hours", title="Hours by Client")
    st.plotly_chart(fig3, use_container_width=True)

    df_time["Week"] = df_time["Date"].dt.isocalendar().week
    df_time["Month"] = df_time["Date"].dt.to_period("M").astype(str)

    weekly = df_time.groupby("Week")["Hours"].sum().reset_index()
    monthly = df_time.groupby("Month")["Hours"].sum().reset_index()

    fig4 = px.bar(weekly, x="Week", y="Hours", title="Weekly Hours")
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.bar(monthly, x="Month", y="Hours", title="Monthly Hours")
    st.plotly_chart(fig5, use_container_width=True)

# ---------------- Export ----------------
st.header("Export Report")
if st.button("Export to Excel"):
    df_time.to_excel("Time_Report.xlsx", index=False)
    st.success("Report Exported")

st.write("Last updated:", datetime.now())
