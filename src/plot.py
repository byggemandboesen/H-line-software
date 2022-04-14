import imageio
import numpy as np
from datetime import datetime
from matplotlib import colors
import matplotlib.pyplot as plt

class Plotter():
    def __init__(self, **kwargs):
        self.SHOW_MAP = kwargs["plot_map"]
        self.Y_MIN = kwargs["y_min"]
        self.Y_MAX = kwargs["y_max"]

        # Constants
        self.H_FREQUENCY = 1420405750
        self.C_SPEED = 299792.458 # km/s

    def plot(self, freqs, data, **kwargs):
        # Unpack info
        ra, dec = kwargs["ra"], kwargs["dec"]
        observer_vel = kwargs["obs_vel"]
        SNR, doppler = kwargs["SNR"], kwargs["doppler"]

        if self.SHOW_MAP:
            name = f'ra={ra},dec={dec}'
            fig = plt.figure(figsize=(20,12))
            fig.suptitle('H-line observation', fontsize = 22, y = 0.99)
            grid = fig.add_gridspec(2,2)

            details_ax = fig.add_subplot(grid[0,0])
            sky_ax = fig.add_subplot(grid[0,1])
            spectrum_ax = fig.add_subplot(grid[1,:])

            self.spectrumGrid(spectrum_ax, freqs, data)
            self.skyGrid(sky_ax, ra, dec)
            self.detailsGrid(details_ax, ra, dec, observer_vel,doppler, SNR)
        else:
            name = datetime.utcnow().strftime('D%m%d%YT%H%M%S')
            fig, ax = plt.subplots(figsize = (12, 7))
            self.spectrumGrid(ax, freqs, data)
        

        # Saves plot
        path = f'./Spectrums/{name}.png'
        plt.tight_layout(pad = 1.5)
        plt.savefig(path, dpi = 200)
        plt.close()
        return name

    # Arrange detail grid
    # TODO: Properly center table
    def detailsGrid(self, ax, ra, dec, observer_velocity, doppler, SNR):
        ax.axis('off')

        observer_vel = np.round(observer_velocity, 1)
        source_vel = np.round(doppler - observer_vel, 1)
        title = ['Values']
        labels = ['RA', 'Dec', 'Peak SNR', 'Doppler', 'Observer vel.', 'Source vel.']
        values = [
            [fr'{ra}$^\circ$'],
            [fr'{dec}$^\circ$'],
            [f'{SNR}dB'],
            [f'{doppler}' + r'$\frac{km}{s}$'],
            [f'{observer_vel}' + r'$\frac{km}{s}$'],
            [f'{source_vel}' + r'$\frac{km}{s}$']]

        loc = 'center'
        colwidth = [0.4, 0.1]
        color = [colors.to_rgba('g', 0.4)]*6

        table = ax.table(cellText = values, colLabels = title, rowLabels = labels, colColours = color, rowColours = color, rowLoc = loc, cellLoc = loc, loc = 9, colWidths = colwidth)
        table.set_fontsize(16)
        table.scale(1.25, 3.25)
    
    
    # Arrange sky grid
    def skyGrid(self, ax, ra, dec):
        ax.set(title = 'Milky Way H-line map')

        # Huge thanks to the Virgo and Pictor project for sharing their code for the hydrogen line map!
        img = np.loadtxt('map.txt')
        flipimg = np.flip(img, 1)
        ax.imshow(flipimg, extent = [360, 0, -90, 90], interpolation = 'none')

        # Axis labels
        ax.set(xlabel = 'Right ascension / degrees', ylabel = 'Declination / degrees')
        ax.axvline(x = ra, color = 'r', linestyle = ':', linewidth = 1)
        ax.axhline(y = dec, color = 'r', linestyle = ':', linewidth = 1)

        # Plot with legend
        ax.plot(ra, dec, marker = '.', markersize = 15, color = 'r', label = 'LAB HI Survey (Kalberla et al., 2005)')
        ax.legend(prop = {'size': 10}, loc = 1)


    # Arranges spectrum grid
    def spectrumGrid(self, ax, freqs, data):
        start_freq = freqs[0]
        stop_freq = freqs[-1]

        ax.plot(freqs, data, color = 'g', label = 'Observed data')

        # Plots theoretical H-line frequency
        ax.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', linewidth = 2, label = 'Theoretical frequency')
        
        # Sets axis labels and adds legend & grid
        ylabel ='Signal to noise ratio (SNR) / dB'
        xlabel = 'Frequency / Hz'
        title = 'FFT spectrum'

        ax.set(xlabel = xlabel, ylabel = ylabel, title = title)
        ax.set(xlim = [start_freq, stop_freq])
        ax.legend(prop = {'size': 10}, loc = 1)
        ax.grid()

        # Adds y-axis interval if supplied in config.txt
        if 0.0 == self.Y_MIN == self.Y_MAX:
            ax.autoscale(enable = True, axis = 'y')
        else:
            ax.set(ylim = [self.Y_MIN, self.Y_MAX])

        # Adds top x-axis for doppler
        doppler = ax.secondary_xaxis('top', functions =(self.dopplerFromFreq, self.freqFromDoppler))
        doppler.set_xlabel(r'Observed doppler / $\frac{km}{s}$')


    # Returns the doppler and maximum SNR
    def getDoppler(self, data, freqs):
        # Center around H-line
        min_index = (np.abs(np.array(freqs)-1419750000)).argmin()
        max_index = (np.abs(np.array(freqs)-1421200000)).argmin()

        SNR = np.amax(data[min_index:max_index])
        #Get index of max SNR
        index = np.where(data==SNR)[0][0]
        doppler = self.dopplerFromFreq(freqs[index])

        return np.round(SNR, 2), np.round(doppler, 2)


    # Returns doppler from frequency
    def dopplerFromFreq(self, freq):
        diff_freq = freq - self.H_FREQUENCY
        v_doppler = self.C_SPEED*diff_freq/self.H_FREQUENCY
        return v_doppler
    

    # Returns frequency from doppler
    def freqFromDoppler(self, doppler):
        diff_freq = doppler*self.H_FREQUENCY/self.C_SPEED
        freq = diff_freq+self.H_FREQUENCY
        return freq