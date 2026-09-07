import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time

# Configure page for mobile responsiveness
st.set_page_config(
    page_title="Versova Fleet Dashboard",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Mobile View
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
        .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Initialize fleet data in Session State (preserves baseline across updates)
if "fleet_df" not in st.session_state:
    np.random.seed(42)
    boat_names = [f"Versova Star {i}" for i in range(1, 11)]
    status_list = ["At Sea", "Docked", "Maintenance", "At Sea", "At Sea"]
    
    initial_data = []
    for name in boat_names:
        status = np.random.choice(status_list)
        # Versova Beach Base Coordinates: ~19.1351° N, 72.8015° E
        lat = 19.1351 + (np.random.uniform(-0.04, -0.01) if status == "At Sea" else 0.0)
        lon = 72.8015 + (np.random.uniform(-0.04, -0.01) if status == "At Sea" else 0.0)
        fuel = float(np.random.randint(40, 95)) if status != "Maintenance" else float(np.random.randint(10, 25))
        catch_kg = int(np.random.randint(100, 400)) if status == "At Sea" else 0
        
        initial_data.append({
            "Boat Name": name,
            "Status": status,
            "latitude": lat,
            "longitude": lon,
            "Fuel (%)": fuel,
            "Catch Today (kg)": catch_kg,
            "Last Signal": datetime.datetime.now().strftime("%H:%M:%S")
        })
    st.session_state.fleet_df = pd.DataFrame(initial_data)

# Function to update boat metrics incrementally
def update_fleet_metrics(df):
    updated_rows = []
    for idx, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        fuel = row["Fuel (%)"]
        catch = row["Catch Today (kg)"]
        status = row["Status"]

        if status == "At Sea":
            # Small, subtle spatial drift (~10-50 meters)
            lat += np.random.uniform(-0.0005, 0.0005)
            lon += np.random.uniform(-0.0005, 0.0005)
            # Slight fuel drain (0.1% - 0.4%)
            fuel = max(0.0, fuel - np.random.uniform(0.1, 0.4))
            # Occasional small catch increase (0 to 5 kg)
            catch += np.random.choice([0, 1, 2, 5], p=[0.5, 0.25, 0.15, 0.10])
        elif status == "Docked":
            # Slight fuel refill if refuel underway
            fuel = min(100.0, fuel + np.random.uniform(0.0, 0.2))

        updated_rows.append({
            "Boat Name": row["Boat Name"],
            "Status": status,
            "latitude": lat,
            "longitude": lon,
            "Fuel (%)": round(fuel, 1),
            "Catch Today (kg)": catch,
            "Last Signal": datetime.datetime.now().strftime("%H:%M:%S")
        })
    return pd.DataFrame(updated_rows)

# Dynamic Dashboard UI Container
dashboard_container = st.empty()

# Live Loop updating every 10 seconds
while True:
    # Update DataFrame values with minor variance
    st.session_state.fleet_df = update_fleet_metrics(st.session_state.fleet_df)
    df = st.session_state.fleet_df

    with dashboard_container.container():
        st.title("⚓ Versova Fleet Dashboard")
        st.caption(f"Live monitoring • Auto-refreshing every 10s • Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")

        st.divider()

        # Metrics Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Active at Sea", len(df[df["Status"] == "At Sea"]))
        col2.metric("Docked at Shore", len(df[df["Status"] == "Docked"]))
        col3.metric("In Maintenance", len(df[df["Status"] == "Maintenance"]))
        col4.metric("Total Catch (Kg)", f"{df['Catch Today (kg)'].sum():,}")

        st.divider()

        # Map Display
        st.subheader("📍 Live Vessel Locations (Versova Waters)")
        st.map(df[["latitude", "longitude"]], zoom=12, use_container_width=True)

        # Vessel Table
        st.subheader("🚢 Fleet Details")
        st.dataframe(
            df[["Boat Name", "Status", "Fuel (%)", "Catch Today (kg)", "Last Signal"]],
            hide_index=True,
            use_container_width=True
        )

        # Fuel Alerts
        low_fuel = df[df["Fuel (%)"] < 25]
        if not low_fuel.empty:
            st.warning(f"⚠️ **Low Fuel Alert**: {', '.join(low_fuel['Boat Name'].tolist())}")

    # Wait 10 seconds before looping next frame update
    time.sleep(10)
