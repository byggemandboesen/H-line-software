import subprocess
import json
import os
import textwrap
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
        "median": 3
    },
    "observer": {
        "latitude": 0.0,
        "longitude": 0.0,
        "azimuth": 0.0,
        "altitude": 0.0
    },
    "plotting":{
        "plot_map": False,
        "y_min": 0.0,
        "y_max": 0.0
    },
    "observation": {
        "24h": False,
        "degree_interval": 5.0,
        "debug": False
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

#Callback functions
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
    elif sender == "update_parameters":
        print("Fetching parameters from config.json")
        read_from_config()
    elif sender == "edit_theme":
        dpg.show_style_editor()
    elif sender == "open_obs_folder":
        path = f"{os.getcwd()}/Spectrums/"
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])


# Handle checkbox actions
def checkbox_callback(sender, app_data, user_data):
    parameters[user_data][sender] = app_data

# Handle text actions
def text_callback(sender, app_data, user_data):
    parameters[user_data][sender] = round(app_data,3) if isinstance(app_data, float) else app_data

def dropdown_callback(sender, app_data, user_data):
    parameters[user_data][sender] = int(app_data)

# Run user intereface
def run_ui():
    dpg.create_context()
    dpg.create_viewport(title='H-Line software - By Victor Boesen', width=650, height=500)
    
    # Generate window for SDR and DSP parameters
    # Each parameter can be found in config.json
    with dpg.window(label="SDR and DSP parameters",width=300,height=280,pos=(10,10),no_resize=True,no_close=True,no_move=True):
        # RTL-TCP section
        with dpg.group(horizontal=True):
            dpg.add_text("RTL-TCP parameters")
            dpg.add_text("(help)",tag="RTL-TCP_category")

        # Host server
        with dpg.group(horizontal=True):
            dpg.add_button(label="Host server",tag="TCP_host",user_data="SDR",callback=btn_callback)
            dpg.add_text("Click to host server")

        # Create option for connecting to host
        with dpg.group(horizontal=True):
            dpg.add_checkbox(label="Connnect to host",user_data="SDR",callback=checkbox_callback,tag="connect_to_host")
            dpg.add_input_text(label="IP of host",user_data="SDR",default_value="127.0.0.1",tag="host_IP",callback=text_callback)
        dpg.add_spacer(height=5)

        with dpg.tooltip("RTL-TCP_category"):
            help_msg = '''
            Host server = Host server on this device.
            Connect to host = Connect to remote host.
            IP of host = IP of remote host.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

        # RTL-SDR section
        with dpg.group(horizontal=True):
            dpg.add_text("RTL-SDR parameters")
            dpg.add_text("(help)",tag="RTL-SDR_category")

        dpg.add_combo(SAMPLE_RATES,label="Sample rate",user_data="SDR",default_value=2400000,tag="sample_rate",callback=dropdown_callback)
        dpg.add_input_int(label="Resolution",user_data="SDR",default_value=11,tag="resolution",callback=text_callback)
        dpg.add_input_int(label="PPM offset",user_data="SDR",default_value=0,tag="PPM_offset",callback=text_callback)
        dpg.add_spacer(height=5)

        with dpg.tooltip("RTL-SDR_category"):
            help_msg = '''
            Sample rate = Sample rate of SDR. Values above 2.4MSPS may cause sample drops.
            Resolution = 2^Resolution samples are collected pr. FFT.
            PPM offset = Offset of the RTL-SDR local oscillator in parts per million.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

        # DSP section
        with dpg.group(horizontal=True):
            dpg.add_text("DSP parameters")
            dpg.add_text("(help)",tag="DSP_category")

        dpg.add_input_int(label="FFT number",user_data="DSP",default_value=1000,tag="number_of_fft",callback=text_callback)
        dpg.add_input_int(label="Median",user_data="DSP",default_value=3,tag="median",callback=text_callback)

        with dpg.tooltip("DSP_category"):
            help_msg = '''
            FFT number = Number of FFT's to receive and average.
            Median = Number of samples to include in median smoothing.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

    # Generate window for observer and plotting parameters
    with dpg.window(label="Observer and plot parameters",width=300,height=280,pos=(320,10),no_resize=True,no_close=True,no_move=True):
        # Observer section
        with dpg.group(horizontal=True):
            dpg.add_text("Observer parameters")
            dpg.add_text("(help)", tag="observer_category")
        dpg.add_input_float(label="Latitude",user_data="observer",tag="latitude",callback=text_callback,default_value=0.0)
        dpg.add_input_float(label="Longitude",user_data="observer",tag="longitude",callback=text_callback,default_value=0.0)
        
        dpg.add_input_float(label="Azimuth",user_data="observer",tag="azimuth",callback=text_callback,default_value=0.0)
        dpg.add_input_float(label="Altitude",user_data="observer",tag="altitude",callback=text_callback,default_value=0.0)
        dpg.add_spacer(height=5)

        # Show tooltip when hovered above
        with dpg.tooltip("observer_category"):
            help_msg = '''
            Latitude/longitude = Position of observer position.
            Lat in [-90,90], Lon in [-180,180], where east and north is positive.
            Azimuth/altitude = Direction of antenna position.
            Azimuth in [0,360] going east from north. Altitude in [0,90].
            '''
            dpg.add_text(textwrap.dedent(help_msg))

        # Plotting section
        with dpg.group(horizontal=True):
            dpg.add_text("Plotting parameters")
            dpg.add_text("(help)",tag="plotting_category")

        dpg.add_checkbox(label="Plot galactic map",user_data="plotting",tag="plot_map",default_value=False,callback=checkbox_callback)
        dpg.add_input_float(label="Y-min",user_data="plotting",tag="y_min",callback=text_callback,default_value=0.0)
        dpg.add_input_float(label="Y-max",user_data="plotting",tag="y_max",callback=text_callback,default_value=0.0)
        dpg.add_spacer(height=5)

        with dpg.tooltip("plotting_category"):
            help_msg = '''
            Plot galactic map = Shows a map and doppler information together with your spectrum.
            Y-min and Y-max = Set the y-axis plotting range.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

    # Observations parameters (fx. 24h observation and debug)
    with dpg.window(label="Observation",width=300,height=150,pos=(10,300),no_resize=True,no_close=True,no_move=True):
        with dpg.group(horizontal=True):
            dpg.add_text("Observation parameters")
            dpg.add_text("(help)",tag="observation_category")
        
        dpg.add_checkbox(label="24H observation",tag="24h",user_data="observation",default_value=False,callback=checkbox_callback)
        dpg.add_input_float(label="Deg. interval",tag="degree_interval",user_data="observation",default_value=5.0,callback=text_callback)
        dpg.add_checkbox(label="Debug",tag="debug",user_data="observation",callback=checkbox_callback,default_value=False)
        dpg.add_button(label="Run observation",tag="run_observation",callback=btn_callback)

        with dpg.tooltip("observation_category"):
            help_msg = '''
            24H observation = Perform observations for 24 hours.
            Deg. interval = Interval between each observation in degrees.
            Debug = Include debug data from observation.
            '''
            dpg.add_text(textwrap.dedent(help_msg))
    
    # Update values, change theme and etc.
    with dpg.window(label="Actions", width=300,height=150,pos=(320,300),no_resize=True,no_close=True,no_move=True):
        with dpg.group(horizontal=True):
            dpg.add_text("Perform actions")
            dpg.add_text("(help)", tag="action_category")
        
        dpg.add_button(label="Edit theme",tag="edit_theme",callback=btn_callback)
        dpg.add_button(label="Browse observations",tag="open_obs_folder",callback=btn_callback)
        dpg.add_button(label="Update parameters from config",tag="update_parameters",callback=btn_callback)

        with dpg.tooltip("action_category"):
            help_msg = '''
            Edit theme = Edit the look and appearance of the user interface
            Browse observations = Browse the folder with previous observations
            Update parameters from config = Updates the UI with the parameters from the config file
            '''
            dpg.add_text(textwrap.dedent(help_msg))


    # TODO Show map of current antenna direction in Milky way
    # with dpg.window(label="Current position in Milky Way",width=680,height=280,pos=(300,10),no_resize=True,no_close=True):
    #     dpg.add_button(label="Update map", tag="update_map",callback=btn_callback)

    # TODO Maybe show latest observation
    # This will not work yet, since the images are saved in too high resolution
    # with dpg.window(label="Latest observation", width=680,height=580,pos=(300,10),no_resize=True,no_close=True):
    #     width, height, channels, data = dpg.load_image("Spectrums/ra=304.3,dec=39.9.png")
    #     dpg.add_button(label="Update",tag="update_observation", callback=btn_callback)
    #     dpg.add_static_texture(width, height, data)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    print("Launching user interface!")
    run_ui()