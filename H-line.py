import contextlib
import os, sys, json
from time import sleep
from datetime import datetime, timedelta

# Import necessary classes/modules
sys.path.append("src/")
from rtl import RTL
from plot import Plotter
from ephem import Coordinates
from dsp import DSP
from analysis import Analysis


# Main method
def main(config):
    clear_console()
    SDR_PARAM = config["SDR"]
    DSP_PARAM = config["DSP"]
    OBSERVER_PARAM = config["observer"]
    PLOTTING_PARAM = config["plotting"]
    OBSERVATION_PARAM = config["observation"]

    # Define some classes:
    RTL_CLASS = RTL(**SDR_PARAM)
    DSP_CLASS = DSP(**DSP_PARAM)
    PLOT_CLASS = Plotter(**PLOTTING_PARAM)
    
    # Does user want this device to act as RTL-TCP host? If yes - start host
    if SDR_PARAM["TCP_host"]:
        RTL_CLASS.tcpHost()
        quit()
    
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

    # Get information from config
    lat, lon = OBSERVER_PARAM['latitude'], OBSERVER_PARAM['longitude']
    alt, az = OBSERVER_PARAM['altitude'], OBSERVER_PARAM['azimuth']
    OBSERVER_CLASS = Coordinates(lat, lon)
    
    # Get ra/dec and etc for observer
    ra, dec = OBSERVER_CLASS.equatorial(alt, az)
    # gal_lat, gal_lon = OBSERVER.galactic(alt, az)
    
    # Get SDR
    if SDR_PARAM["connect_to_host"]:
        sdr = RTL_CLASS.rtlTcpClient()
    else:
        sdr = RTL_CLASS.rtlClient()

    # Check if it should observe for 24H
    if OBSERVATION_PARAM["24h"]:
        ra_list = [ra]
        # Calculate list of all RA values for each observation
        # We don't want the RA > 360 hence the if statements below
        for i in range(1, int(num_data)):
            ra_list.append(round(ra_list[i-1] + deg_interval if ra_list[i-1] + deg_interval <= 360.0 else deg_interval - (360.0 - ra_list[i-1]), 1))
        
        # Now, observe
        current_time = datetime.utcnow()
        for i in range (num_data):
            print(f"Started observing! - {datetime.utcnow()}")
            print(f"Receiving {DSP_PARAM['number_of_fft']} FFT's of {2**DSP_PARAM['resolution']} samples")
            with contextlib.redirect_stdout(None):
                observe(DSP_CLASS, OBSERVER_CLASS, SDR_PARAM, DSP_PARAM, PLOTTING_PARAM, OBSERVATION_PARAM["debug"], sdr, ra_list[i], dec)
            print(f"Done observing! - {datetime.utcnow()}")

            # Wait for next execution
            clear_console()
            end_time = current_time + timedelta(seconds = second_interval * (i + 1))
            time_remaining = end_time - datetime.utcnow()
            print(f'Waiting for next data collection in {time_remaining.total_seconds()} seconds')
            sleep(time_remaining.total_seconds())
        
        PLOT_CLASS.generateGIF(ra=ra_list,dec=dec)
    else:
        print(f"Started observing! - {datetime.utcnow()}")
        print(f"Receiving {DSP_PARAM['number_of_fft']} FFT's of {2**DSP_PARAM['resolution']} samples")
        # with contextlib.redirect_stdout(None):
        observe(DSP_CLASS, OBSERVER_CLASS, SDR_PARAM, DSP_PARAM, PLOTTING_PARAM, OBSERVATION_PARAM["debug"], sdr, ra, dec)
        print(f"Done observing! - {datetime.utcnow()}")


# Perform observation
# TODO Make this easier and not messy
def observe(DSP_CLASS, OBS_CLASS, SDR_PARAM, DSP_PARAM, PLOTTING_PARAM, debug, sdr, ra, dec):
    freqs = DSP_CLASS.generateFreqs(sample_rate = SDR_PARAM["sample_rate"])
    h_line_data = DSP_CLASS.sample(sdr)
    
    # Sample blank
    sdr.center_freq += 3200000
    blank_data = DSP_CLASS.sample(sdr)

    # Get SNR spectrum, correct for slant and apply median filter
    SNR_spectrum = DSP_CLASS.combineSpectrums(freqs = freqs, h_line_data = h_line_data, blank_data = blank_data)
    SNR_spectrum = DSP_CLASS.correctSlant(SNR_spectrum)
    if DSP_PARAM["median"] != 0:
        SNR_spectrum = DSP_CLASS.applyMedian(SNR_spectrum)

    PLOT_CLASS = Plotter(**PLOTTING_PARAM)
    ANALYSIS_CLASS = Analysis()
    # Get radial velocity and maximum SNR
    max_SNR, radial_velocity = ANALYSIS_CLASS.getRadialVelocity(SNR_spectrum,freqs)

    # Get frequency corrections w.r.t. barycenter and Local Standard of Rest
    barycenter_vel_correction = OBS_CLASS.barycenterVelocityCorrection(ra, dec)
    vel_wrt_barycenter = radial_velocity - barycenter_vel_correction
    lsr_vel_correction = OBS_CLASS.lsrVelocityCorrection(ra, dec, vel_wrt_barycenter)

    plot_info = {
        "ra": ra,
        "dec": dec,
        "barycenter_correction": barycenter_vel_correction,
        "lsr_correction": lsr_vel_correction,
        "SNR": max_SNR,
        "radial_velocity": radial_velocity
    }
    obs_name = PLOT_CLASS.plot(freqs=freqs,data=SNR_spectrum,**plot_info)
    
    if debug:
        print("Writing debug file!")
        writeDebug(freqs, SNR_spectrum, h_line_data, blank_data, SDR_PARAM, DSP_PARAM, obs_name, **plot_info)


# Write debug file
def writeDebug(freqs, SNR_spectrum, h_line_spectrum, blank_spectrum, SDR_PARAM, DSP_PARAM, obs_name, **kwargs):
    ra, dec = kwargs["ra"], kwargs["dec"]
    SNR, radial_velocity = kwargs["SNR"], kwargs["radial_velocity"]
    barycenter_correction, lsr_correction = kwargs["barycenter_correction"], kwargs["lsr_correction"]

    json_file = {
        "SDR Parameters": SDR_PARAM,
        "DSP Parameters": DSP_PARAM,
        "Observation results": {
            "RA": ra,
            "Dec": dec,
            "Radial velocity": radial_velocity,
            "Barycenter correction": barycenter_correction,
            "LSR correction": lsr_correction,
            "Max SNR": SNR
        },
        "Data": {
            "Blank spectrum": blank_spectrum.tolist(),
            "H-line spectrum": h_line_spectrum.tolist(),
            "SNR Spectrum": SNR_spectrum.tolist(),
            "Frequency list": freqs.tolist()
        }
    }

    # Save file
    with open(f"Spectrums/debug({obs_name}).json", "w") as file:
        json.dump(json_file, file, indent = 4)


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
