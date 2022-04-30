import contextlib
import os, sys, json
from time import sleep
from datetime import datetime, timedelta

# Import necessary classes/modules
sys.path.append("src/")
from observation import Observation as obs


# Main method
def main(config):
    clear_console()
    SDR_PARAM = config["SDR"]
    DSP_PARAM = config["DSP"]
    OBSERVER_PARAM = config["observer"]
    PLOTTING_PARAM = config["plotting"]
    OBSERVATION_PARAM = config["observation"]

    Observation = obs(**OBSERVATION_PARAM)

    sdr = Observation.getSDR(**SDR_PARAM)

    # If user wants 24h observations
    if OBSERVATION_PARAM["24h"]:
        # Checks if 360 is divisable with the degree interval and calculates number of collections
        try:
            deg_interval = OBSERVATION_PARAM["degree_interval"]
            num_data = int(360/deg_interval) if (360/deg_interval).is_integer() else ValueError
            second_interval = 24*60**2/num_data
        except:
            print("Degree interval not divisable with 360 degrees")
            quit()
    else:
        num_data = 1

    # Do observation(s)
    # Start time of observation
    current_time = datetime.utcnow()
    for i in range(num_data):
        COORD_CLASS = Observation.getCoordinates(current_time + timedelta(seconds = 24*60**2/num_data * i), **OBSERVER_PARAM)
        print(current_time + timedelta(seconds = 24*60**2/num_data * i))
        
        print(f"Started observing! - {current_time}")
        print(f"Receiving {DSP_PARAM['number_of_fft']} FFT's of {2**DSP_PARAM['resolution']} samples")

        with contextlib.redirect_stdout(None):
            Observation.collectData(sdr, SDR_PARAM["sample_rate"], **DSP_PARAM)
        print("Analyzing data...")
        Observation.analyzeData(COORD_CLASS)
        print("Plotting data...")
        Observation.plotData(**PLOTTING_PARAM)

        print(f"Done observing! - {datetime.utcnow()}")

        # Next, write datafile if necessary
        if OBSERVATION_PARAM["datafile"]:
            user_params = {
                "SDR": SDR_PARAM,
                "DSP": DSP_PARAM,
                "Observer": OBSERVER_PARAM,
                "Observation": OBSERVATION_PARAM
            }
            Observation.writeDatafile(**user_params)

        # Wait for next execution
        if num_data > 1:
            end_time = current_time + timedelta(seconds = second_interval * (i + 1))
            time_remaining = end_time - datetime.utcnow()
            print(f'Waiting for next data collection in {time_remaining.total_seconds()} seconds')
            sleep(time_remaining.total_seconds())
            clear_console()


# Reads user config
def read_config():
    path = 'config.json'
    config = open(path, 'r')
    parsed_config = json.load(config)
    main(parsed_config)


# For clearing console
def clear_console():
    os.system('cls' if os.name =='nt' else 'clear')


if __name__ == "__main__":
    read_config()
