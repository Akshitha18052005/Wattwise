import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta

st.set_page_config(page_title="WATTWISE", page_icon="⚡", layout="wide")

# ---------- Demo data ----------
APPLIANCES = ["Air Conditioner", "Refrigerator", "Washing Machine", "Kettle", "TV", "Lights"]

MONTHS = ["May", "June", "July", "August", "September", "October"]
MONTHLY_KWH = [126, 139, 151, 144, 158, 171]
MONTHLY_COST = [1008, 1112, 1208, 1152, 1264, 1368]

def appliance_data():
    return pd.DataFrame({
        "Appliance": APPLIANCES,
        "Energy (kWh)": [72.4, 31.8, 18.6, 10.2, 16.7, 21.3],
        "Cost (₹)": [579, 254, 149, 82, 134, 170],
        "Usage (hours)": [118, 744, 14, 17, 92, 210]
    })

def daily_data():
    days = pd.date_range("2026-10-01", "2026-10-07")
    kwh = [5.2, 5.8, 6.1, 5.4, 7.0, 6.5, 6.0]
    return pd.DataFrame({"Date": days, "Energy (kWh)": kwh})

def hourly_data():
    hours = list(range(24))
    power = [180,160,150,145,140,150,220,480,620,410,280,240,
             230,260,300,330,420,680,920,810,620,430,300,220]
    return pd.DataFrame({"Hour": hours, "Power (W)": power})

# ---------- Session / login ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def login_page():
    st.markdown("# ⚡ WATTWISE")
    st.markdown("### Smart appliance energy monitoring")
    st.caption("Monitor household energy use from one main measurement point.")

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary", use_container_width=True):
            if email == "demo@wattwise.app" and password == "WattWise@123":
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid login. For the demo use demo@wattwise.app / WattWise@123.")

    with tab2:
        name = st.text_input("Full name")
        email2 = st.text_input("Email address")
        p1 = st.text_input("Create password", type="password")
        p2 = st.text_input("Confirm password", type="password")
        if st.button("Create Account", use_container_width=True):
            if not name or not email2 or not p1:
                st.warning("Please complete all fields.")
            elif p1 != p2:
                st.error("Passwords do not match.")
            elif len(p1) < 8:
                st.error("Password should contain at least 8 characters.")
            else:
                st.success("Account created for this prototype. You can now log in with the demo account to explore the dashboard.")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------- Main app ----------
with st.sidebar:
    st.markdown("## ⚡ WATTWISE")
    st.caption(f"Signed in as {st.session_state.user_email}")
    page = st.radio("Menu", ["Dashboard", "Live Usage", "Appliance Usage", "History", "Alerts", "Profile"])
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

rate = 8.0
df_app = appliance_data()
total_kwh = float(df_app["Energy (kWh)"].sum())
total_cost = float(df_app["Cost (₹)"].sum())
previous_kwh = 158.0
change = (total_kwh - previous_kwh) / previous_kwh * 100

if page == "Dashboard":
    st.title("Dashboard")
    st.caption("October 2026 • Household energy overview")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("This Month", f"{total_kwh:.1f} kWh", f"{change:+.1f}% vs Sep")
    c2.metric("Estimated Cost", f"₹{total_cost:,.0f}")
    c3.metric("Highest Consumer", "Air Conditioner")
    c4.metric("Peak Power", "920 W")

    st.subheader("Monthly Consumption")
    import plotly.express as px
    mdf = pd.DataFrame({"Month": MONTHS, "Energy (kWh)": MONTHLY_KWH})
    fig = px.line(mdf, x="Month", y="Energy (kWh)", markers=True, title="Energy trend")
    st.plotly_chart(fig, use_container_width=True)

    left,right = st.columns(2)
    with left:
        st.subheader("Appliance-wise Energy")
        fig2 = px.bar(df_app, x="Appliance", y="Energy (kWh)", title="Consumption by appliance")
        st.plotly_chart(fig2, use_container_width=True)
    with right:
        st.subheader("Cost by Appliance")
        fig3 = px.pie(df_app, names="Appliance", values="Cost (₹)", title="Estimated electricity cost")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Recent Usage")
    ddf = daily_data()
    fig4 = px.area(ddf, x="Date", y="Energy (kWh)", title="Daily energy consumption")
    st.plotly_chart(fig4, use_container_width=True)

elif page == "Live Usage":
    st.title("Live Usage")
    st.caption("This screen represents the user-side view of readings received from the main-line sensor.")
    hdf = hourly_data()
    current_power = int(hdf.iloc[-1]["Power (W)"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Current Power", f"{current_power} W")
    c2.metric("Today's Energy", "6.0 kWh")
    c3.metric("Today's Estimated Cost", "₹48")
    import plotly.express as px
    fig = px.line(hdf, x="Hour", y="Power (W)", markers=True, title="Power usage across the day")
    st.plotly_chart(fig, use_container_width=True)
    st.info("In the final hardware version, this data will come from the ESP32 + clamp current sensor. The NILM model will estimate individual appliance loads from the aggregate reading.")

elif page == "Appliance Usage":
    st.title("Appliance Usage")
    st.caption("Estimated appliance-level consumption from the aggregate household signal.")
    st.dataframe(df_app, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select appliance", APPLIANCES)
    row = df_app[df_app["Appliance"] == selected].iloc[0]
    a,b,c = st.columns(3)
    a.metric("Energy", f"{row['Energy (kWh)']:.1f} kWh")
    b.metric("Estimated Cost", f"₹{row['Cost (₹)']:.0f}")
    c.metric("Usage", f"{row['Usage (hours)']:.0f} hrs")
    st.success(f"{selected} is currently estimated from the household aggregate signal.")

elif page == "History":
    st.title("Consumption History")
    month = st.selectbox("Select month", MONTHS[::-1])
    idx = MONTHS.index(month)
    kwh = MONTHLY_KWH[idx]
    cost = MONTHLY_COST[idx]
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Energy", f"{kwh} kWh")
    c2.metric("Estimated Cost", f"₹{cost:,}")
    if idx > 0:
        diff = kwh - MONTHLY_KWH[idx-1]
        c3.metric("Compared with previous month", f"{diff:+.0f} kWh")
    else:
        c3.metric("Compared with previous month", "—")
    st.subheader(f"{month} appliance summary")
    hist = df_app.copy()
    factor = kwh / total_kwh
    hist["Energy (kWh)"] = (hist["Energy (kWh)"] * factor).round(1)
    hist["Cost (₹)"] = (hist["Energy (kWh)"] * rate).round(0)
    st.dataframe(hist, use_container_width=True, hide_index=True)
    import plotly.express as px
    fig = px.bar(hist, x="Appliance", y="Energy (kWh)", title=f"{month} appliance consumption")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Alerts":
    st.title("Alerts & Insights")
    st.warning("⚠️ Air Conditioner is your highest energy-consuming appliance this month.")
    st.info("💡 This month is about 8.2% higher than September.")
    st.success("✓ Refrigerator usage is within its normal range.")
    st.subheader("Recommended actions")
    st.write("• Check prolonged AC usage during peak hours.")
    st.write("• Review appliances with unusual increases.")
    st.write("• Compare this month with previous months before changing usage habits.")

elif page == "Profile":
    st.title("Profile & Settings")
    st.write(f"**Account:** {st.session_state.user_email}")
    st.text_input("Name", value="Demo User")
    st.number_input("Electricity tariff (₹/kWh)", value=8.0, min_value=1.0, step=0.5)
    st.selectbox("Preferred report", ["Monthly", "Weekly", "Daily"])
    st.button("Save Settings")
    st.caption("For a production version, authentication and user records should be stored securely in a backend database.")
