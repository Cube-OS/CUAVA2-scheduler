import os
import datetime
# import requests
import subprocess
import time
from utils import fetch_tle, predict_next_pass, utc_to_local
import argparse
import pytz
import logging
import psutil

def setup_logging(log_dir):
    log_filename = os.path.join(log_dir, datetime.datetime.now().strftime("%m%d_%H:%M.txt"))
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

def kill_process_and_children(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def main():

    # # Determine the script's directory
    # script_dir = os.path.dirname(os.path.abspath(__file__))

    satellite_name = "WS-1"
    satellite_id = "60469"
    # satellite_id, satellite_name = get_user_choice()

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

    # Create a new folder with the current date and time
    log_dir = datetime.datetime.now().strftime("%m%d_%H:%M")
    os.makedirs(log_dir, exist_ok=True)

    setup_logging(log_dir)

    # Start isis-ground with the specified satellite name
    process_isisground = subprocess.Popen(["/home/cuava/Ops/isis-ground-new", "-s", satellite_name])
    pid_1 = process_isisground.pid
    logging.info(f"Started isis-ground with PID: {pid_1}")
    print(f"Started isis-ground with PID: {pid_1}")
   
    gs_autorun_path = "/home/cuava/Ops/gs-autorun"
    pass_ws_path = "/home/cuava/Ops/pass_ws.txt"

    gs_autorun_log_path = os.path.join(log_dir, 'gs-autorun.log')
    with open(gs_autorun_log_path, 'w') as gs_log:
        process_gsautorun = subprocess.Popen(
            [gs_autorun_path, "-i", pass_ws_path,"-t","8"],
            stdout=gs_log,
            stderr=gs_log,
            cwd="/home/cuava/Ops"
        )
    # process_gsautorun = subprocess.Popen(["/home/cuava/Ops/gs-autorun", "-i", "pass_cuava_rc.txt"])    
    pid_2 = process_gsautorun.pid
    logging.info(f"Started gs-autorun with PID: {pid_2}")
    print(f"Started gs-autorun with PID: {pid_2}")
    
    # Wait for process_2 to complete
    #  process_gsautorun.wait()

    # Wait for 2 minutes and then check if process_2 is still running
    time.sleep(180)  # Wait for 2 minutes
    if process_gsautorun.poll() is None:  # Check if process_2 is still running
        kill_process_and_children(pid_2)   # Terminate gs-autorun
        
        logging.info(f"Terminated gs-autorun with PID: {pid_2} after 3 minutes")
        print(f"Terminated gs-autorun with PID: {pid_2} after 3 minutes")
    else:
        logging.info("gs-autorun completed successfully.")
        print("gs-autorun completed successfully.")
  
    for i in range(3):
        file_client_log_path = os.path.join(log_dir, f'file-client-{i+1}.log')
        with open(file_client_log_path, 'w') as ftp_log:
            process_ftp = subprocess.Popen(
                ["/home/cuava/Ops/file-client", "-P", "8040", "-p", "8000", "-c", "100", "download"],
                stdout=ftp_log,
                stderr=ftp_log
            )
        pid_3 = process_ftp.pid
        logging.info(f"Started file-client instance {i+1} with PID: {pid_3}")
        print(f"Started file-client instance {i+1} with PID: {pid_3}")

        time.sleep(120)  # Wait for 2 minute
        if process_ftp.poll() is None:  # Check if process_ftp is still running
            os.kill(pid_3, 15)  # Terminate file-client
            logging.info(f"Terminated file-client instance {i+1} with PID: {pid_3} after 1 minute")
            print(f"Terminated file-client instance {i+1} with PID: {pid_3} after 1 minute")
        else:
            logging.info(f"file-client instance {i+1} completed successfully.")
            print(f"file-client instance {i+1} completed successfully.")

    # # Wait until the predicted pass time
    # time_to_wait = (next_pass_utc - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds()
    # time.sleep(max(0, time_to_wait))
    
    time.sleep(60)
    os.kill(pid_1, 15)  # Terminate isis-ground
    os.kill(pid_3, 15)  # Terminate file-client
    
    logging.info("Terminated all processes.")
    print("Terminated all processes.")


if __name__ == "__main__":
    main()
