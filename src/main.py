import os
import datetime
# import requests
import subprocess
import time
from utils import fetch_tle, predict_next_pass, utc_to_local
import argparse
import pytz
import logging

def setup_logging():
    log_filename = datetime.datetime.now().strftime("%m-%d_%H-%M.txt")
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')

def get_user_choice():
    parser = argparse.ArgumentParser(description='Fetch TLE data for a satellite.')
    parser.add_argument('-s', '--satellite', type=str, required=True, help='Name of the satellite')
    args = parser.parse_args()

    if args.satellite == "CUAVA-2":
        return '60527', 'CUAVA-2'
    elif args.satellite == "WS-1":
        return '60469', 'WS-1'
    else:
        raise ValueError(f"Unknown satellite name: {args.satellite}")

def main():
    setup_logging()

    # Create a new folder with the current date and time
    log_dir = datetime.datetime.now().strftime("%Y%m%d_%H:%M")
    os.makedirs(log_dir, exist_ok=True)

    # # Determine the script's directory
    # script_dir = os.path.dirname(os.path.abspath(__file__))

    # satellite_name = "CUAVA-2"
    # satellite_id = "60527"
    satellite_id, satellite_name = get_user_choice()

    local_tz = 'Australia/Sydney'  

    tle_lines = fetch_tle(satellite_id)
    next_pass_utc = predict_next_pass(tle_lines)
    next_pass_local = utc_to_local(next_pass_utc, local_tz)
    print(f"Next pass over Sydney (Local): {next_pass_local}")

    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    # print(f"Current time (UTC): {utc_now}")
    time_to_wait = (next_pass_utc - utc_now).total_seconds()
    print(f"Waiting for {time_to_wait} seconds until the next pass...")
    
    # time_to_wait = (next_pass_utc - datetime.datetime.utcnow()).total_seconds()
    # print(f"Waiting for {time_to_wait} seconds until the next pass...")
    time.sleep(max(0, time_to_wait))

    process_isisground = subprocess.Popen(["/home/cuava/Ops/isis-ground-new", "-s", satellite_name])
    pid_1 = process_isisground.pid
    logging.info(f"Started isis-ground with PID: {pid_1}")
    print(f"Started isis-ground with PID: {pid_1}")
   
    gs_autorun_path = "/home/cuava/Ops/gs-autorun"
    pass_cuava_rc_path = "/home/cuava/Ops/pass_cuava_rc.txt"

    gs_autorun_log_path = os.path.join(log_dir, 'gs-autorun.log')
    with open(gs_autorun_log_path, 'w') as gs_log:
        process_gsautorun = subprocess.Popen(
            [gs_autorun_path, "-i", pass_cuava_rc_path,"-t", "10"],
            stdout=gs_log,
            stderr=gs_log,
            cwd="/home/cuava/Ops"
        )
    pid_2 = process_gsautorun.pid
    logging.info(f"Started gs-autorun with PID: {pid_2}")
    print(f"Started gs-autorun with PID: {pid_2}")
    
    # Wait for 2 minutes and then check if process_2 is still running
    time.sleep(300)  # Wait for 5 minutes
    if process_gsautorun.poll() is None:  # Check if process_2 is still running
        os.kill(pid_2, 15)  # Terminate gs-autorun
        logging.info(f"Terminated gs-autorun with PID: {pid_2} after 5 minutes")
        print(f"Terminated gs-autorun with PID: {pid_2} after 5 minutes")
    else:
        logging.info("gs-autorun completed successfully.")
        print("gs-autorun completed successfully.")
    
    # # Wait for process_2 to complete
    # process_gsautorun.wait()
  
    file_client_log_path = os.path.join(log_dir, 'file-client.log')    
    with open(file_client_log_path, 'w') as ftp_log:
        process_ftp = subprocess.Popen(
            ["/home/cuava/Ops/file-client", "-P", "8040", "-p", "8000", "-c", "100", "download"],
            stdout=ftp_log,
            stderr=ftp_log
        )
    pid_3 = process_ftp.pid
    logging.info(f"Started file-client with PID: {pid_3}")
    print(f"Started file-client with PID: {pid_3}")

    # # Wait until the predicted pass time
    # time_to_wait = (next_pass_utc - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds()
    # time.sleep(max(0, time_to_wait))
    
    time.sleep(600)  # Wait for 10 minutes
    os.kill(pid_1, 15)  # Terminate isis-ground
    os.kill(pid_3, 15)  # Terminate file-client
    
    logging.info("Terminated all processes.")
    print("Terminated all processes.")


if __name__ == "__main__":
    main()