import os
import numpy as np
from Ephem import Coordinates
import matplotlib.pyplot as plt
from matplotlib.pyplot import GridSpec
from matplotlib import colors
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
        name = f'ra={ra},dec={dec}'

        if 'none' in (ra, dec):
            fig, ax = plt.subplots(figsize = (12, 7))
            self.spectrum_grid(ax, low_y, high_y)
        else:
            fig = plt.figure(figsize=(20,12))
            fig.suptitle('H-line observation', fontsize = 20)
            grid = fig.add_gridspec(2,2)

            details_ax = fig.add_subplot(grid[0, 0])
            sky_ax = fig.add_subplot(grid[0, 1])
            spectrum_ax = fig.add_subplot(grid[1, :])

            self.spectrum_grid(spectrum_ax, low_y, high_y)
            self.sky_grid(sky_ax, ra, dec)
            self.detail_grid(details_ax, ra, dec)

        
        # Saves plot
        path = f'./Spectrums/{name}.png'
        plt.tight_layout()
        plt.savefig(path, dpi = 300)
        plt.close()


    # Arrange detail grid
    # TODO: Properly center table
    def detail_grid(self, ax, ra, dec):
        ax.axis('off')

        SNR, doppler = self.SNR_and_doppler()
        title = ['Parameters']
        labels = ['RA', 'Dec', 'SNR', 'Doppler']
        values = [
            [fr'{ra}$^\circ$'],
            [fr'{dec}$^\circ$'],
            [f'{SNR}dB'],
            [f'{doppler}' + r'$\frac{km}{s}$']]

        loc = 'center'
        colwidth = [0.5, 0.1]
        color = [colors.to_rgba('g', 0.4)]*4

        table = ax.table(cellText = values, colLabels = title, rowLabels = labels, colColours = color, rowColours = color, rowLoc = loc, cellLoc = loc, loc = 9, colWidths = colwidth)
        table.set_fontsize(22)
        # Adjust font size inside cells
        # cells = table.get_celld()
        # cells[(1,0)].set_fontsize(10)

        # for key, cell in table.get_celld().items():
        #     if key[1] == 0 and key[0] != 0:
        #         cell.set_fontsize(10)
        #         print(key, cell.get_text().get_text())
            

        table.scale(1.5, 3)
    
    
    # Arrange sky grid
    def sky_grid(self, ax, ra, dec):
        ax.set(title = 'Milky Way H-line map')

        # Huge thanks to the Virgo and Pictor project for sharing their code for the hydrogen line map!
        img = np.loadtxt('map.txt')
        flipimg = np.flip(img, 1)
        ax.imshow(flipimg, extent = [360, 0, -90, 90], interpolation = 'none')

        # Set x- and y-ticks for RA, Dec coordinates
        # ax.set(xlim = (0, 360), ylim = (-90, 90))
        # RA_ticks = [0, 1, 2, 3, 4, 5, 6]
        # RA_labels = [0, 60, 120, 180, 240, 300, 360]
        # Dec_ticks = [0, 1, 2, 3, 4, 5, 6]
        # Dec_labels = [-90, -60, -30, 0, 30, 60, 90]
        # ax.set(xticks = RA_ticks, xticklabels = RA_labels, xlabel = 'Right ascension / degrees')
        # ax.set(yticks = Dec_ticks, yticklabels = Dec_labels, ylabel = 'Declination / degrees')

        ax.axvline(x = ra, color = 'r', linestyle = ':', linewidth = 1)
        ax.axhline(y = dec, color = 'r', linestyle = ':', linewidth = 1)
        # TODO: Fix axis ticks and labels
        ax.plot(ra, dec, marker = '.', markersize = 15, color = 'r', label = 'LAB HI Survey (Kalberla et al., 2005)')
        ax.legend(prop = {'size': 10})
        



    # Arranges spectrum grid
    def spectrum_grid(self, ax, low_y, high_y):
        start_freq = self.freqs[0]
        stop_freq = self.freqs[-1]
        SNR, doppler = self.SNR_and_doppler()
        # obj_vel = round(self.galactic_velocity - doppler, 1)

        ax.plot(self.freqs, self.data, color = 'g', label = 'Observed data')

        # Plots theoretical H-line frequency
        ax.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', linewidth = 2, label = 'Theoretical frequency')
        
        # Sets axis labels and adds legend & grid
        ylabel ='Signal to noise ratio (SNR) / dB'
        xlabel = 'Frequency / Hz'
        title = 'FFT spectrum'

        ax.set(xlabel = xlabel, ylabel = ylabel, title = title)
        ax.set(xlim = [start_freq, stop_freq])
        ax.legend(prop = {'size': 10})
        ax.grid()

        # Adds y-axis interval if supplied in config.txt
        if not "none" in (low_y, high_y):
            ax.set(ylim = [low_y, high_y])

        # Adds top x-axis for doppler
        # TODO Correct doppler from galactical coordinates
        doppler = ax.secondary_xaxis('top', functions =(self.doppler_from_freq, self.freq_from_doppler))
        doppler.set_xlabel(r'Relative doppler / $\frac{km}{s}$')


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

