import os
import matplotlib.pyplot as plt

from datetime import datetime

class Plot:
    def __init__(self):
        self.H_FREQUENCY = 1420405000

    def plot(self, freqs, data, name):
        start_freq = freqs[0]
        stop_freq = freqs[-1]


        plt.plot(freqs, data, color = 'g', label = 'Observed data')

        # Checks if H-line is included in frequency range
        if start_freq < self.H_FREQUENCY and stop_freq > self.H_FREQUENCY:
            plt.axvline(x = self.H_FREQUENCY, color = 'r', linestyle = ':', label = 'Theoretical frequency')
            ylabel ='Signal to noise ratio (SNR) / dB'
            plt.title(name)
        else:
            ylabel = 'Relative power / dB'

        plt.grid()
        plt.legend(prop = {'size': 8})
        plt.xlabel('Frequency / Hz')
        plt.xlim([start_freq, stop_freq])            
        plt.ylabel(ylabel)

        '''
        freq_path = './FREQS.txt'
        PSD_path = './PSD.txt'

        file_psd = open(PSD_path, 'w')
        file_psd.writelines(str(averaged_PSD))
        file_psd.close()
        '''
        
        path = f'./Spectrums/{name}.png'
        plt.savefig(path, dpi = 300)

        # Show image
        # os.system('./Spectrums/fft.png')
