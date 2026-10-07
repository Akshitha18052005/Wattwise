# WATTWISE — User-Side Working Prototype

A software-only prototype for the WATTWISE NILM project.

## What this prototype demonstrates
- User registration and login with password validation
- Dashboard with current month consumption
- Previous month comparison
- Appliance-wise estimated energy and cost
- Daily consumption chart
- Hourly/current-use view
- Historical monthly reports
- High-consumption alerts
- Profile/logout flow
- Demo data so the application works without ESP32 hardware

## Run
1. Install Python 3.10+
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## Important
This is a working UI/prototype using demo household data. It does NOT claim that the demo values are live sensor readings.
Later, replace the demo-data layer with ESP32 + clamp-current-sensor readings and the trained NILM model.

Demo login:
Email: demo@wattwise.app
Password: WattWise@123
