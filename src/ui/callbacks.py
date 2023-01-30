import subprocess
import json
import os
import dearpygui.dearpygui as dpg

# Define sample rates
SAMPLE_RATES = [3200000,2800000,2560000,2400000,2048000,1920000,1800000,1400000,1024000,900001,250000]

# Define default parameters
parameters = {
    "SDR": {
        "sample_rate": 2400000,
        "PPM_offset": 0,
        "TCP_host": False,
        "connect_to_host": False,
        "host_IP": "127.0.0.1"
    },
    "DSP": {
        "number_of_fft": 1000,
        "resolution": 11,
        "median": 5
    },
    "observer": {
        "latitude": 0.0,
        "longitude": 0.0,
        "azimuth": 0.0,
        "altitude": 0.0,
        "elevation": 0.0
    },
    "plotting":{
        "plot_map": True,
        "y_min": 0.0,
        "y_max": 0.0
    },
    "observation": {
        "24h": False,
        "degree_interval": 5.0,
        "datafile": False
    }
}


# Write parameters to config
def update_config():
    with open("config.json", "w+") as config_file:
        json.dump(parameters, config_file, indent=4)

# Update parameters from config file
def read_from_config():
    with open("config.json", "r") as config_file:
        parsed_config = json.load(config_file)
        categories = list(parsed_config.keys())
        
        # Iterrate over each key in category (SDR, DSP, etc.)
        for category in categories:
            for key, value in parsed_config[category].items():
                dpg.set_value(key, value)
                parameters[category][key] = value

# Callback functions
# Handle button actions
def btn_callback(sender, app_data, user_data):
    if sender == "TCP_host":
        parameters[user_data][sender] = True
        update_config()
        os.system('py H-line.py' if os.name =='nt' else 'python3 H-line.py')
        parameters[user_data][sender] = False
        update_config()
    elif sender == "run_observation":
        update_config()
        os.system('py H-line.py' if os.name =='nt' else 'python3 H-line.py')
    elif sender == "edit_theme":
        dpg.show_style_editor()
    elif sender == "open_obs_folder":
        path = f"{os.getcwd()}/Spectrums/"
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
    elif sender == "update_parameters":
        print("Fetching parameters from config.json")
        read_from_config()

# Handle checkbox actions
def checkbox_callback(sender, app_data, user_data):
    parameters[user_data][sender] = app_data

# Handle text actions
def text_callback(sender, app_data, user_data):
    parameters[user_data][sender] = round(app_data,3) if isinstance(app_data, float) else app_data

def dropdown_callback(sender, app_data, user_data):
    parameters[user_data][sender] = int(app_data)

