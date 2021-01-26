import os
import matplotlib.pyplot as plt

from datetime import datetime

class Plot:
    def __init__(self, freqs, data):
        self.H_FREQUENCY = 1420405000
        self.c_speed = 299792.458
        self.freqs = freqs
        self.data = data

    def plot(self, name):
        start_freq = self.freqs[0]
        stop_freq = self.freqs[-1]

        fig, ax = plt.subplots(figsize=(16,9))
        ax.plot(self.freqs, self.data, color = 'g', label = 'Observed data')

        # Plots theoretical H-line frequency
        ax.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', label = 'Theoretical frequency')
        ylabel ='Signal to noise ratio (SNR) / dB'
        xlabel = 'Frequency / Hz'
        ax.set(title = name, xlabel = xlabel, ylabel = ylabel)
        ax.set(xlim = [start_freq, stop_freq])
        ax.legend(prop = {'size': 8})
        ax.grid()

        # Adds top x-axis for doppler
        # TODO Correct doppler from galactical coordinates
        doppler = ax.secondary_xaxis('top', functions =(self.doppler_from_freq, self.freq_from_doppler))
        doppler.set_xlabel('Doppler / km/s')

        '''
        freq_path = './FREQS.txt'
        PSD_path = './PSD.txt'

        file_psd = open(PSD_path, 'w')
        file_psd.writelines(str(averaged_PSD))
        file_psd.close()
        '''
        
        path = f'./Spectrums/{name}.png'
        plt.savefig(path, dpi = 300)
        plt.close()

        # Show image
        # os.system('./Spectrums/fft.png')

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

