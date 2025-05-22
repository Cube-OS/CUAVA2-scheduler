import os
import requests
from datetime import datetime, timedelta
import pytz
# from sgp4.api import Satrec, jday
# from sgp4.api import SGP4_ERRORS
# import predict
from skyfield.api import EarthSatellite, Topos, load


def fetch_tle(satellite_name):
    tle_file_path = f'/home/cuava/Ops/tle/{satellite_name}.txt'
    if not os.path.exists(tle_file_path):
        raise FileNotFoundError(f"TLE file for {satellite_name} not found at {tle_file_path}")
    
    response = requests.get(f'https://celestrak.com/NORAD/elements/gp.php?CATNR={satellite_name}')
    tle_lines = response.text.strip().split('\n')
    
    if len(tle_lines) != 3:
        raise ValueError(f"Invalid TLE data for {satellite_name}")
    
    return [line.strip() for line in tle_lines]

def predict_next_pass(tle_lines):
    gs_location = Topos('33.8688 S', '151.2093 E')  # Sydney

    satellite = EarthSatellite(tle_lines[1], tle_lines[2], tle_lines[0], load.timescale())
    ground_station = gs_location

    ts = load.timescale()
    now = ts.utc(datetime.utcnow().replace(tzinfo=pytz.utc))
    t0 = now
    t1 = ts.utc((datetime.utcnow() + timedelta(hours=14)).replace(tzinfo=pytz.utc))

    times, events = satellite.find_events(ground_station, t0, t1, altitude_degrees=20.0)

    if len(events) == 0:
        raise RuntimeError("No passes found in the next 12 hours")

    # Start the pass 2 minutes early as the prediction is done for 10deg altitude   
    next_pass_utc = times[0].utc_datetime() - timedelta(minutes=2)  

    # test
    # next_pass_utc = datetime.utcnow().replace(tzinfo=pytz.utc) 
    return next_pass_utc

def utc_to_local(utc_dt, local_tz):
    local_tz = pytz.timezone(local_tz)
    return utc_dt.astimezone(local_tz)

# def execute_command(command):
#     process = os.popen(command)
#     return process.pid

# def terminate_process(pid):
#     os.kill(pid, 9)  # Force terminate the process
