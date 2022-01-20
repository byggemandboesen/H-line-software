import imageio
import numpy as np
from datetime import datetime
from matplotlib import colors
import matplotlib.pyplot as plt

class Plot:

    def __init__(self, freqs, data, observer_velocity):
        self.H_FREQUENCY = 1420405000
        self.c_speed = 299792.458 # km/s
        self.freqs = freqs
        self.data = data
        self.observer_velocity = observer_velocity

    def plot(self, ra, dec, low_y, high_y):

        if 'none' in (ra, dec):
            name = datetime.utcnow().strftime('D%m%d%YT%H%M%S')
            fig, ax = plt.subplots(figsize = (12, 7))
            self.spectrum_grid(ax, low_y, high_y)
        else:
            name = f'ra={ra},dec={dec}'
            fig = plt.figure(figsize=(20,12))
            fig.suptitle('H-line observation', fontsize = 22, y = 0.99)
            grid = fig.add_gridspec(2,2)

            details_ax = fig.add_subplot(grid[0, 0])
            sky_ax = fig.add_subplot(grid[0, 1])
            spectrum_ax = fig.add_subplot(grid[1, :])

            self.spectrum_grid(spectrum_ax, low_y, high_y)
            self.sky_grid(sky_ax, ra, dec)
            self.detail_grid(details_ax, ra, dec)

        
        # Saves plot
        path = f'./Spectrums/{name}.png'
        plt.tight_layout(pad = 1.5)
        plt.savefig(path, dpi = 300)
        plt.close()


    # Arrange detail grid
    # TODO: Properly center table
    def detail_grid(self, ax, ra, dec):
        ax.axis('off')

        SNR, doppler = self.SNR_and_doppler()
        observer_vel = round(self.observer_velocity, 1)
        source_vel = round(doppler - observer_vel, 1)
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
    def sky_grid(self, ax, ra, dec):
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
    def spectrum_grid(self, ax, low_y, high_y):
        start_freq = self.freqs[0]
        stop_freq = self.freqs[-1]
        SNR, doppler = self.SNR_and_doppler()

        ax.plot(self.freqs, self.data, color = 'g', label = 'Observed data')

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
        if not "none" in (low_y, high_y):
            ax.set(ylim = [low_y, high_y])
        else:
            ax.autoscale(enable = True, axis = 'y')

        # Adds top x-axis for doppler
        doppler = ax.secondary_xaxis('top', functions =(self.doppler_from_freq, self.freq_from_doppler))
        doppler.set_xlabel(r'Observed doppler / $\frac{km}{s}$')


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


    # Generates and saves a GIF of 24H observations
    def generate_GIF(self, ra, dec):
        print('Generating GIF from observations... This may take a while')
        path = f'Spectrums/ra={ra[0]},dec={dec}.gif'
        images = [imageio.imread(f'Spectrums/ra={coord},dec={dec}.png') for coord in ra]
        imageio.mimsave(path, images)
