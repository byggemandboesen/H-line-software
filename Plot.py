import os
import numpy as np
from Ephem import Coordinates
import matplotlib.pyplot as plt
from matplotlib.pyplot import GridSpec
from datetime import datetime


# TODO Plot map and antenna direction

class Plot:
    def __init__(self, freqs, data, galactic_velocity):
        self.H_FREQUENCY = 1420405000
        self.c_speed = 299792.458 # km/s
        self.freqs = freqs
        self.data = data
        self.galactic_velocity = galactic_velocity

    def plot(self, ra, dec, low_y, high_y):
        start_freq = self.freqs[0]
        stop_freq = self.freqs[-1]
        SNR, doppler = self.SNR_and_doppler()
        obj_vel = round(self.galactic_velocity - doppler, 1)
        name = f'ra={ra}, dec={dec}, SNR={SNR}, doppler={doppler}, obj. velocity={obj_vel}'

        fig, ax = plt.subplots(figsize=(12,7))
        ax.plot(self.freqs, self.data, color = 'g', label = 'Observed data')

        # Plots theoretical H-line frequency
        ax.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', label = 'Theoretical frequency')
        
        # Sets axis labels and adds legend & grid
        ylabel ='Signal to noise ratio (SNR) / dB'
        xlabel = 'Frequency / Hz'
        ax.set(title = name, xlabel = xlabel, ylabel = ylabel)
        ax.set(xlim = [start_freq, stop_freq])
        ax.legend(prop = {'size': 8})
        ax.grid()

        # Adds y-axis interval if supplied in config.txt
        if not "none" in (low_y, high_y):
            ax.set(ylim = [low_y, high_y])

        # Adds top x-axis for doppler
        # TODO Correct doppler from galactical coordinates
        doppler = ax.secondary_xaxis('top', functions =(self.doppler_from_freq, self.freq_from_doppler))
        doppler.set_xlabel(r'Relative doppler / $\frac{km}{s}$')
        
        # Saves plot
        path = f'./Spectrums/{name}.png'
        plt.tight_layout()
        plt.savefig(path, dpi = 300)
        plt.close()


    # Returns highest SNR and doppler of the highest peak    
    def SNR_and_doppler(self):
        data = self.data
        freqs = self.freqs

        # Finds SNR in isolated area around the H-line to avoid calculating SNR from noise
        min_index = (np.abs(freqs-self.freq_from_doppler(-120))).argmin()
        max_index = (np.abs(freqs-self.freq_from_doppler(120))).argmin()
        SNR = max(data[min_index:max_index])
        SNR_index = list(data).index(SNR)

        doppler = self.doppler_from_freq(freqs[SNR_index])
        return round(SNR, 3), round(doppler, 1)


    # Returns doppler from frequency
    def doppler_from_freq(self, freq):
        diff_freq = freq - self.H_FREQUENCY
        v_doppler = self.c_speed*diff_freq/self.H_FREQUENCY
        return v_doppler
    

    # Returns frequency from doppler
    def freq_from_doppler(self, doppler):
        diff_freq = doppler*self.H_FREQUENCY/self.c_speed
        freq = diff_freq+self.H_FREQUENCY
        return freq

