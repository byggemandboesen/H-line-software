import os, sys, json, contextlib
from time import sleep
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Due to Receive.py not wanting to be importet we add src to path
sys.path.append("src/")
from rtl import RTL
from plot import Plotter
from Ephem import Coordinates
from dsp import DSP


# Reads user config
def read_config():
    path = 'config.json'
    config = open(path, 'r')
    parsed_config = json.load(config)
    main(parsed_config)


# Main method
def main(config):
    SDR_PARAM = config["SDR"]
    DSP_PARAM = config["DSP"]
    OBSERVER_PARAM = config["observer"]
    PLOTTING_PARAM = config["plotting"]
    OBSERVATION_PARAM = config["observation"]

    # Define some classes:
    RTL_CLASS = RTL(**SDR_PARAM)
    DSP_CLASS = DSP(**DSP_PARAM)
    
    # Does user want this device to act as RTL-TCP host? If yes - start host
    if SDR_PARAM["TCP_host"]:
        RTL_CLASS.tcpHost()
        quit()
    
    # If user wants 24h observations
    if OBSERVATION_PARAM["24h"]:
        # Checks if 360 is divisable with the degree interval and calculates number of collections
        try:
            deg_interval = OBSERVATION_PARAM["degree_interval"]
            num_data = int(360/deg_interval) if 360 % deg_interval == 0 else ValueError
            second_interval = 24*60**2/num_data
        except:
            print("Degree interval not divisable with 360 degrees")
            quit()
    else:
        num_data = 1

    # Get information from config if necessary (when plot map is checked)
    if PLOTTING_PARAM["plot_map"]:
        lat, lon = OBSERVER_PARAM['latitude'], OBSERVER_PARAM['longitude']
        alt, az = OBSERVER_PARAM['altitude'], OBSERVER_PARAM['azimuth']
        OBSERVER = Coordinates(lat, lon, alt, az)
        
        # Get ra/dec and etc for observer
        ra, dec = OBSERVER.equatorial()
        gal_lat, gal_lon = OBSERVER.galactic()
        observer_velocity = OBSERVER.observer_velocity(gal_lat, gal_lon)

        # Now, get list of RA coordinates for each observation:
        if OBSERVATION_PARAM["24h"]:
            ra_list = [ra]
            # We don't want the RA > 360 hence the if statements below
            for i in range(1, int(num_data)):
                ra_list.append(round(ra_list[i-1] + deg_interval if ra_list[i-1] + deg_interval <= 360.0 else deg_interval - (360.0 - ra_list[i-1]), 1))
    
    # Get SDR
    if SDR_PARAM["connect_to_host"]:
        sdr = RTL_CLASS.rtlTcpClient()
    else:
        sdr = RTL_CLASS.rtlClient()
    
    # Perform observations
    # TODO Basically allow for the bellow to happen with 24H observations
    # current_time = datetime.utcnow()
    freqs = DSP_CLASS.generateFreqs(sample_rate = SDR_PARAM["sample_rate"])
    h_line_data = DSP_CLASS.sample(sdr)
    
    # Sample blank
    sdr.center_freq += 3000000
    blank_data = DSP_CLASS.sample(sdr)

    SNR_spectrum, max_SNR = DSP_CLASS.computeSNR(freqs = freqs, h_line_data = h_line_data, blank_data = blank_data)
    if DSP_PARAM["median"] != 0:
        SNR_spectrum = DSP_CLASS.applyMedian(SNR_spectrum)
    
    plt.plot(SNR_spectrum)
    plt.show()
    # Now, plot the data
    # PLOT_CLASS = Plotter(**PLOTTING_PARAM)
    # TODO Plot that sheit!!


'''
    if float(num_data).is_integer():
        # Set coordinates for each observation if possible
        if 0.0 == lat == lon == alt == az:
            ra, dec = 'none', 'none'
            observer_velocity = 'N/A'
        else:
            # Get current equatorial and galactic coordinates of antenna RA and Declination
            Coordinates_class = Coordinates(lat = lat, lon = lon, alt = alt, az = az)
            ra, dec = Coordinates_class.equatorial(num_data, args.interval)
            gal_lat, gal_lon = Coordinates_class.galactic()
            observer_velocity = Coordinates_class.observer_velocity(gal_lat, gal_lon)
        
        # Current time of first data collection
        current_time = datetime.utcnow()
        num_data = int(num_data)
        
        # Check if one or multiple observations are planned
        if num_data == 0:
            # Perform only ONE observation
            freqs, data = observe(args)
            if args.debug:
                write_debug(freqs, data, args, ra, dec)
            plot(freqs, data, ra, dec, low_y, high_y, observer_velocity)
        else:
            # Perform multiple observations for 24 hours
            for i in range (num_data):
                freqs, data = observe(args)
                plot(freqs, data, ra[i], dec, low_y, high_y, observer_velocity)

                # Wait for next execution
                clear_console()
                end_time = current_time + timedelta(seconds = second_interval * (i + 1))
                time_remaining = end_time - datetime.utcnow()
                print(f'Waiting for next data collection in {time_remaining.total_seconds()} seconds')
                sleep(time_remaining.total_seconds())
            
            # Generate GIF from observations
            Plot_class = Plot(freqs = freqs, data = data, observer_velocity = observer_velocity)
            Plot_class.generate_GIF(ra[0], dec)
            
    else:
        print('360 must be divisable with the degree interval. Eg. the quotient must be a positive natural number (1, 2, 3, and not 3.4)')
        quit()
'''

# # Write debug file
# # TODO Add raw data in this file as well
# def write_debug(freqs, data, args, ra, dec):
#     parameters = {
#         "sample_rate": args.sample_rate,
#         "ppm": args.ppm,
#         "resolution": args.resolution,
#         "num_FFT": args.num_FFT,
#         "num_med": args.num_med
#     }
#     if not isinstance(data, list):
#         data = data.tolist()
#     data = {
#         "Freqs": freqs.tolist(),
#         "Data": data
#     }
#     json_file = {"Parameters": parameters, "Data": data}

#     if "none" in (ra, dec):
#         stamp = datetime.utcnow().strftime('D%m%d%YT%H%M%S')
#     else:
#         stamp = f'ra={ra},dec={dec}'

#     with open(f"Spectrums/debug({stamp}).json", "w") as file:
#         json.dump(json_file, file, indent = 4)


def clear_console():
    os.system('cls' if os.name =='nt' else 'clear')

if __name__ == "__main__":
    read_config()
