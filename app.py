import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Configure page for mobile responsiveness
st.set_page_config(
    page_title="Versova Fleet Management",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Mobile View
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
        .stMetric { background-color: #0090BF; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Generate Mock Data for Versova Beach Fleet (Lat: 19.1351, Lon: 72.8015)
@st.cache_data
def load_fleet_data():
    np.random.seed(42)
    boat_names = [f"Versova Star {i}" for i in range(1, 11)]
    status_list = ["At Sea", "Docked", "Maintenance", "At Sea", "At Sea"]
    
    data = []
    for name in boat_names:
        status = np.random.choice(status_list)
        # Randomize offset near Versova coastline
        lat = 19.1351 + (np.random.uniform(-0.04, 0.02) if status == "At Sea" else 0.0)
        lon = 72.8015 + (np.random.uniform(-0.05, 0.00) if status == "At Sea" else 0.0)
        fuel = np.random.randint(20, 100) if status != "Maintenance" else np.random.randint(5, 25)
        catch_kg = np.random.randint(100, 850) if status == "At Sea" else 0
        
        data.append({
            "Boat Name": name,
            "Status": status,
            "latitude": lat,
            "longitude": lon,
            "Fuel (%)": fuel,
            "Catch Today (kg)": catch_kg,
            "Last Signal": datetime.datetime.now().strftime("%H:%M:%S")
        })
    return pd.DataFrame(data)

df = load_fleet_data()

# Header & Quick Refresh
st.title("⚓ Versova Fleet Dashboard")
st.caption("Real-time monitoring of fishing vessels at Versova Landing Centre")

if st.button("🔄 Refresh Location Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.divider()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active at Sea", len(df[df["Status"] == "At Sea"]))
col2.metric("Docked at Shore", len(df[df["Status"] == "Docked"]))
col3.metric("In Maintenance", len(df[df["Status"] == "Maintenance"]))
col4.metric("Total Catch (Kg)", f"{df['Catch Today (kg)'].sum():,}")

st.divider()

# Vessel Location Map
st.subheader("📍 Vessel Locations (Arabian Sea / Versova Shore)")
st.map(df[["latitude", "longitude"]], zoom=11, use_container_width=True)

# Fleet Details Table
st.subheader("🚢 Fleet Details")

# Status Filter
status_filter = st.multiselect(
    "Filter by Status:",
    options=df["Status"].unique(),
    default=df["Status"].unique()
)

filtered_df = df[df["Status"].isin(status_filter)]

st.dataframe(
    filtered_df[["Boat Name", "Status", "Fuel (%)", "Catch Today (kg)", "Last Signal"]],
    hide_index=True,
    use_container_width=True
)

# Quick Alert Section
low_fuel_boats = df[df["Fuel (%)"] < 25]
if not low_fuel_boats.empty:
    st.warning(f"⚠️ **Low Fuel Alert**: {', '.join(low_fuel_boats['Boat Name'].tolist())} have less than 25% fuel remaining.")
