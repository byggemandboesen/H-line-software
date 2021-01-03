import operator
import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt

import Plot

# Available sample rates
'''
3200000Hz
2800000Hz
2560000Hz
2400000Hz
2048000Hz
1920000Hz
1800000Hz
1400000Hz
1024000Hz
900001Hz
250000Hz
'''

# Receiver claqss. This needs receiving parameters and will write data which can later be processed in "Plot.py"
class Receiver:
    
    def __init__(self, frequency, sample_rate, ppm, resolution, num_FFT):
        self.sdr = RtlSdr()

        # configure SDR
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = frequency
        # For some reason the SDR doesn't want to set the offset PPM to 0 so we avoid that
        if ppm != 0:
            self.sdr.freq_correction = ppm
        self.sdr.gain = 'auto'

        self.resolution = 2**resolution
        self.num_FFT = num_FFT
    
    # Reads data from SDR, processes and writes it
    def receive(self):
        print(f'Receiving {self.num_FFT} samples...')
        averaged_PSD = self.sample()

        # Observed frequency range
        start_freq = self.sdr.center_freq - self.sdr.sample_rate/2
        stop_freq = self.sdr.center_freq + self.sdr.sample_rate/2
        freqs = np.linspace(start = start_freq, stop = stop_freq, num = self.resolution)


        # Corrects the spectrum if the hydrogen line is within the observed frequency range.
        if start_freq < 1420405000 and stop_freq > 1420405000:
            self.sdr.center_freq = self.sdr.center_freq + 3000000
            reference = self.sample()
            averaged_PSD = np.array(reference)/np.array(averaged_PSD)

        # Close the SDR
        self.sdr.close()
        return freqs, averaged_PSD


    # Returns numpy array with PSD values averaged from "num_FFT" datasets
    def sample(self):
        counter = 0.0
        PSD_summed = (0, )* self.resolution
        while (counter < self.num_FFT):
            samples = self.sdr.read_samples(self.resolution)
            
            # Perform FFT and PSD-analysis
            PSD = np.abs(np.fft.fft(samples)/self.sdr.sample_rate)**2
            PSD_log = 10*np.log10(PSD)
            PSD_summed = tuple(map(operator.add, PSD_summed, np.fft.fftshift(PSD_log)))
            
            counter += 1.0
        
        averaged_PSD = tuple(sample/counter for sample in PSD_summed)
        return averaged_PSD
        



