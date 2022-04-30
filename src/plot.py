import imageio
import numpy as np
from matplotlib import colors
import matplotlib.pyplot as plt

from analysis import Analysis
ANALYSIS = Analysis()

class Plotter():
    def __init__(self, plot_map, y_min, y_max):
        self.SHOW_MAP = plot_map
        self.Y_MIN = y_min
        self.Y_MAX = y_max

    def plot(self, freqs, data, **kwargs):
        # Unpack info
        ra, dec = kwargs["ra"], kwargs["dec"]
        gal_lon, gal_lat = kwargs["gal_lon"], kwargs["gal_lat"]
        barycenter_correction = kwargs["barycenter_correction"]
        lsr_correction = kwargs["lsr_correction"]
        freq_correction = ANALYSIS.freqFromRadialVel(barycenter_correction + lsr_correction) - ANALYSIS.H_FREQUENCY
        SNR, radial_velocity = kwargs["SNR"], kwargs["observed_radial_velocity"]

        if self.SHOW_MAP:
            fig = plt.figure(figsize=(20,12))
            fig.suptitle('Hydrogen line observation', fontsize = 22, y = 0.99)
            fig.subplots_adjust(hspace=1)
            grid = fig.add_gridspec(2,2)

            details_ax = fig.add_subplot(grid[0,0])
            sky_ax = fig.add_subplot(grid[0,1])
            spectrum_ax = fig.add_subplot(grid[1,0])
            corrected_spectrum_ax = fig.add_subplot(grid[1,1])

            self.spectrumGrid(spectrum_ax, 'Observed spectrum', freqs, data)
            self.spectrumGrid(corrected_spectrum_ax, 'Corrected spectrum w.r.t. LSR', np.add(freqs, freq_correction), data)
            self.skyGrid(sky_ax, ra, dec)
            self.detailsGrid(details_ax, ra, dec, gal_lon, gal_lat, barycenter_correction, lsr_correction, radial_velocity, SNR)

            # Share y-axis for spectrums
            corrected_spectrum_ax.set_yticklabels([])
            corrected_spectrum_ax.set_ylabel('')

        else:
            fig, ax = plt.subplots(figsize = (12, 7))
            self.spectrumGrid(ax, "Observed spectrum", freqs, data)
        

        # Saves plot
        path = f'./Spectrums/ra={ra},dec={dec}.png'
        plt.tight_layout(pad = 1.75)
        plt.savefig(path, dpi = 100)
        plt.close()

    
    # Arrange detail grid
    # TODO: Redesign table. Perhaps into two subplots
    def detailsGrid(self, ax, ra, dec,gal_lon, gal_lat, barycenter_correction, lsr_correction, radial_velocity, SNR):
        ax.axis('off')

        source_vel = np.round(radial_velocity + barycenter_correction + lsr_correction, 2)
        title = ['Values']
        labels = [r'RA/Dec', r'Galactic $l$/$b$', 'Peak SNR', 'Observed\nradial velocity', 'Radial correction\nfor barycenter', 'Radial correction\nfor LSR', 'Corrected\nsource velocity']
        values = [
            [fr'RA={ra}$^\circ$, Dec={dec}$^\circ$'],
            [fr'$l$={gal_lon}$^\circ$, $b$={gal_lat}$^\circ$'],
            [f'{SNR}dB'],
            [f'{radial_velocity}' + r'$\frac{km}{s}$'],
            [f'{barycenter_correction}' + r'$\frac{km}{s}$'],
            [f'{lsr_correction}' + r'$\frac{km}{s}$'],
            [f'{source_vel}' + r'$\frac{km}{s}$']]

        loc = 'center'
        colwidth = [0.5, 0.2]
        color = [colors.to_rgba('g', 0.5)]*7

        table = ax.table(cellText = values, colLabels = title, rowLabels = labels, colColours = color, rowColours = color, rowLoc = loc, cellLoc = loc, loc = 9, colWidths = colwidth)
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1, 2.25)
    
    
    # Arrange sky grid
    def skyGrid(self, ax, ra, dec):
        ax.set(title = 'Milky Way H-line map')

        # Huge thanks to the Virgo and Pictor project for sharing their code for the hydrogen line map!
        img = np.loadtxt('src/map.txt')
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
    def spectrumGrid(self, ax, title, freqs, data):
        start_freq = freqs[0]
        stop_freq = freqs[-1]

        ax.plot(freqs, data, color = 'g', label = 'Observed data')

        # Plots theoretical H-line frequency
        ax.axvline(x = ANALYSIS.H_FREQUENCY, color = 'r', linestyle = ':', linewidth = 2, label = 'Theoretical frequency')
        
        # Sets axis labels and adds legend & grid
        ylabel ='Signal to noise ratio (SNR) / dB'
        xlabel = 'Frequency / Hz'
        title = title

        ax.set(xlabel = xlabel, ylabel = ylabel, title = title)
        ax.set(xlim = [start_freq, stop_freq])
        ax.legend(prop = {'size': 10}, loc = 1)
        ax.grid()

        # Adds y-axis interval if supplied in config.txt
        if 0.0 == self.Y_MIN == self.Y_MAX:
            ax.autoscale(enable = True, axis = 'y')
        else:
            ax.set(ylim = [self.Y_MIN, self.Y_MAX])

        # Adds top x-axis for radial velocity
        radial_vel = ax.secondary_xaxis('top', functions = (ANALYSIS.radialVelFromFreq, ANALYSIS.freqFromRadialVel))
        radial_vel.set_xlabel(r'Radial velocity / $\frac{km}{s}$')
        

    # Generates and saves a GIF of 24H observations
    def generateGIF(self, ra, dec):
        print('Generating GIF from observations... This may take a while')
        path = f'Spectrums/ra={ra[0]},dec={dec}.gif'
        images = [imageio.imread(f'Spectrums/ra={coord},dec={dec}.png') for coord in ra]
        imageio.mimsave(path, images)