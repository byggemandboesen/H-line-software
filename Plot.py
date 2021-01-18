import os
import matplotlib.pyplot as plt

from datetime import datetime

class Plot:
    def __init__(self):
        self.H_FREQUENCY = 1420405000

    def plot(self, freqs, data):
        start_freq = freqs[0]
        stop_freq = freqs[-1]


        plt.plot(freqs, data, color = 'g', label = 'Observed data')

        if start_freq < self.H_FREQUENCY and stop_freq > self.H_FREQUENCY:
            plt.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', label = 'Theoretical frequency')

        plt.grid()
        plt.legend(prop = {'size': 8})
        plt.xlabel('Frequency / Hz')
        plt.xlim([start_freq, stop_freq])
        plt.ylabel('Signal to noise ratio (SNR) / dB')

        '''
        freq_path = './FREQS.txt'
        PSD_path = './PSD.txt'

        file_psd = open(PSD_path, 'w')
        file_psd.writelines(str(averaged_PSD))
        file_psd.close()
        '''
        
        path = './Spectrums/fft.png'
        plt.savefig(path, dpi = 300)

        # Show image
        # os.system('C:/Users/victo/Documents/programming-projects/Python/H-line-software/Spectrums/fft.png')
