import dearpygui.dearpygui as dpg
import numpy as np

# Import SDR stuff
from src.dsp import DSP
from src.rtl import RTL

class LiveView():
    def __init__(self):
        self.SDR = RTL(2400000,0,'127.0.0.1')
        self.rtl = self.SDR.rtlClient()
        self.DSP_CLASS = DSP(resolution=10,num_fft=20,median=0)
        self.freqs = self.DSP_CLASS.generateFreqs(self.SDR.SAMPLE_RATE)

    # Update with new data
    def updateSpectrum(self):
        data = self.DSP_CLASS.sample(self.rtl)
        # Update the spectrum with new data
        dpg.set_value("spectrum",[self.freqs, data])
        dpg.set_axis_limits("x_axis",self.freqs[0],self.freqs[-1])

    def closeWindow(self):
        print("Releasing SDR...")
        dpg.delete_item("live_window")
        self.rtl.close()
        del self.DSP_CLASS
        del self.SDR
        dpg.stop_dearpygui()

    # Show spectrum
    def showSpectrum(self):

        with dpg.window(label="Live view",tag="live_window",width=400, height=300,pos=(10,10)):
            # Create plot
            with dpg.plot(height=-25,width=-3,no_mouse_pos=True,no_box_select=True):
                # Create x and y axes
                dpg.add_plot_axis(dpg.mvXAxis, label= "Frequency [Hz]", tag="x_axis",no_gridlines=True,no_tick_marks=True)
                dpg.set_axis_limits("x_axis",self.freqs[0],self.freqs[-1])
                dpg.add_plot_axis(dpg.mvYAxis,tag="y_axis",no_tick_marks=True)

                # Series belong to a y axis
                dpg.add_line_series(self.freqs,np.zeros(len(self.freqs)), parent="y_axis", tag="spectrum")

        while True:
            self.updateSpectrum()
            

    # TODO Fix not being able to run observation after closing live