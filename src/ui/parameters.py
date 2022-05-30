import textwrap
import dearpygui.dearpygui as dpg

# Import callbacks and other stuff
from src.ui import callbacks

def sdrWindow():
    # Each parameter can be found in config.json
    with dpg.window(label="SDR and DSP parameters",width=300,height=280,pos=(10,10),no_resize=True,no_close=True,no_move=True):
        # RTL-TCP section
        with dpg.group(horizontal=True):
            dpg.add_text("RTL-TCP parameters")
            dpg.add_text("(help)",tag="RTL-TCP_category")

        # Host server
        with dpg.group(horizontal=True):
            dpg.add_button(label="Host server",tag="TCP_host",user_data="SDR",callback=callbacks.btn_callback)
            dpg.add_text("Click to host server")

        # Create option for connecting to host
        with dpg.group(horizontal=True):
            dpg.add_checkbox(label="Connnect to host",user_data="SDR",callback=callbacks.checkbox_callback,tag="connect_to_host")
            dpg.add_input_text(label="IP of host",user_data="SDR",default_value="127.0.0.1",tag="host_IP",callback=callbacks.text_callback)
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

        dpg.add_combo(callbacks.SAMPLE_RATES,label="Sample rate",user_data="SDR",default_value=2400000,tag="sample_rate",callback=callbacks.dropdown_callback)
        dpg.add_input_int(label="Resolution",user_data="SDR",default_value=11,tag="resolution",callback=callbacks.text_callback)
        dpg.add_input_int(label="PPM offset",user_data="SDR",default_value=0,tag="PPM_offset",callback=callbacks.text_callback)
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

        dpg.add_input_int(label="FFT number",user_data="DSP",default_value=1000,tag="number_of_fft",callback=callbacks.text_callback)
        dpg.add_input_int(label="Median",user_data="DSP",default_value=5,tag="median",callback=callbacks.text_callback)

        with dpg.tooltip("DSP_category"):
            help_msg = '''
            FFT number = Number of FFT's to receive and average.
            Median = Number of samples to include in median smoothing.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

def observerWindow():
    # Generate window for observer and plotting parameters
    with dpg.window(label="Observer and plot parameters",width=300,height=280,pos=(320,10),no_resize=True,no_close=True,no_move=True):
        # Observer section
        with dpg.group(horizontal=True):
            dpg.add_text("Observer parameters")
            dpg.add_text("(help)", tag="observer_category")
        dpg.add_input_float(label="Latitude",user_data="observer",tag="latitude",callback=callbacks.text_callback,default_value=0.0)
        dpg.add_input_float(label="Longitude",user_data="observer",tag="longitude",callback=callbacks.text_callback,default_value=0.0)
        
        dpg.add_input_float(label="Azimuth",user_data="observer",tag="azimuth",callback=callbacks.text_callback,default_value=0.0)
        dpg.add_input_float(label="Altitude",user_data="observer",tag="altitude",callback=callbacks.text_callback,default_value=0.0)
        
        dpg.add_input_float(label="Elevation",user_data="observer",tag="elevation",callback=callbacks.text_callback,default_value=0.0)
        dpg.add_spacer(height=5)

        # Show tooltip when hovered above
        with dpg.tooltip("observer_category"):
            help_msg = '''
            Latitude/longitude = Position of observer position.
            Lat in [-90,90], Lon in [-180,180], where east and north is positive.
            Azimuth/altitude = Direction of antenna position.
            Azimuth in [0,360] going east from north. Altitude in [0,90].
            Elevation = Elevation above ground in meters.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

        # Plotting section
        with dpg.group(horizontal=True):
            dpg.add_text("Plotting parameters")
            dpg.add_text("(help)",tag="plotting_category")

        dpg.add_checkbox(label="Plot galactic map",user_data="plotting",tag="plot_map",default_value=True,callback=callbacks.checkbox_callback)
        dpg.add_input_float(label="Y-min",user_data="plotting",tag="y_min",callback=callbacks.text_callback,default_value=0.0)
        dpg.add_input_float(label="Y-max",user_data="plotting",tag="y_max",callback=callbacks.text_callback,default_value=0.0)
        dpg.add_spacer(height=5)

        with dpg.tooltip("plotting_category"):
            help_msg = '''
            Plot galactic map = Shows a map and doppler information together with your spectrum.
            Y-min and Y-max = Set the y-axis plotting range.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

def observationWindow():
    # Observations parameters (fx. 24h observation and datafile)
    with dpg.window(label="Observation",width=300,height=150,pos=(10,300),no_resize=True,no_close=True,no_move=True):
        with dpg.group(horizontal=True):
            dpg.add_text("Observation parameters")
            dpg.add_text("(help)",tag="observation_category")
        
        dpg.add_checkbox(label="24H observation",tag="24h",user_data="observation",default_value=False,callback=callbacks.checkbox_callback)
        dpg.add_input_float(label="Deg. interval",tag="degree_interval",user_data="observation",default_value=5.0,callback=callbacks.text_callback)
        dpg.add_checkbox(label="Datafile",tag="datafile",user_data="observation",callback=callbacks.checkbox_callback,default_value=False)
        dpg.add_button(label="Run observation",tag="run_observation",callback=callbacks.btn_callback)

        with dpg.tooltip("observation_category"):
            help_msg = '''
            24H observation = Perform observations for 24 hours.
            Deg. interval = Interval between each observation in degrees.
            Datafile = Include data from the observation in a JSON file.
            '''
            dpg.add_text(textwrap.dedent(help_msg))

def actionsWindow():
    # Update values, change theme and etc.
    with dpg.window(label="Actions", width=300,height=150,pos=(320,300),no_resize=True,no_close=True,no_move=True):
        with dpg.group(horizontal=True):
            dpg.add_text("Perform actions")
            dpg.add_text("(help)", tag="action_category")
        
        # dpg.add_button(label="Live view",tag="live_view",callback=callbacks.btn_callback)
        dpg.add_button(label="Edit theme",tag="edit_theme",callback=callbacks.btn_callback)
        dpg.add_button(label="Browse observations",tag="open_obs_folder",callback=callbacks.btn_callback)
        dpg.add_button(label="Update parameters from config",tag="update_parameters",callback=callbacks.btn_callback)

        with dpg.tooltip("action_category"):
            # Live view = Open a live spectrum for locating the H-line.
            help_msg = '''
            Edit theme = Edit the look and appearance of the user interface.
            Browse observations = Browse the folder with previous observations.
            Update parameters from config = Updates the UI with the parameters from the config file.
            '''
            dpg.add_text(textwrap.dedent(help_msg))
