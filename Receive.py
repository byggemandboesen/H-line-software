import operator
import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt

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

# Receiver class. This needs receiving parameters and will receive data from the SDR
class Receiver:
    
    def __init__(self, sample_rate, ppm, resolution, num_FFT):

        self.sdr = RtlSdr()

        # configure SDR
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = 1420405000
        # For some reason the SDR doesn't want to set the offset PPM to 0 so we avoid that
        if ppm != 0:
            self.sdr.freq_correction = ppm
        self.sdr.gain = 'auto'

        self.resolution = 2**resolution
        self.num_FFT = num_FFT

    
    # Reads data from SDR, processes and writes it
    def receive(self):
        print(f'Receiving {self.num_FFT} samples...')
        data_PSD = self.sample()

        # Observed frequency range
        start_freq = self.sdr.center_freq - self.sdr.sample_rate/2
        stop_freq = self.sdr.center_freq + self.sdr.sample_rate/2
        freqs = np.linspace(start = start_freq, stop = stop_freq, num = self.resolution)


        # Samples a blank spectrum to callibrate spectrum with.
        self.sdr.center_freq = self.sdr.center_freq + 3000000
        blank_PSD = self.sample()
        SNR_spectrum, SNR = self.estimate_SNR(data = data_PSD, blank = blank_PSD)

        # Close the SDR
        self.sdr.close()

        return freqs, SNR_spectrum, SNR


    # Returns numpy array with PSD values averaged from "num_FFT" datasets
    def sample(self):
        counter = 0.0
        PSD_summed = (0, )* self.resolution
        while (counter < self.num_FFT):
            samples = self.sdr.read_samples(self.resolution)
            
            # Perform FFT and PSD-analysis
            PSD = np.abs(np.fft.fft(samples)/self.sdr.sample_rate)**2
            try:
                PSD_log = 10*np.log10(PSD)
            except ValueError:
                PSD_checked = self.check_for_zero(PSD)
                PSD_log = 10*np.log10(PSD_checked)
            
            PSD_summed = tuple(map(operator.add, PSD_summed, np.fft.fftshift(PSD_log)))
            
            counter += 1.0
        
        averaged_PSD = tuple(sample/counter for sample in PSD_summed)
        return averaged_PSD


    # Calculates SNR from spectrum and H-line SNR
    def estimate_SNR(self, data, blank):
        SNR = np.array(data)-np.array(blank)
        # Ghetto noise floor estimate:
        noise_floor = (SNR[0]+SNR[1]+SNR[2]+SNR[3]+SNR[4])/5
        shifted_SNR = SNR-noise_floor
        H_SNR = max(shifted_SNR)

        return shifted_SNR, round(H_SNR, 5)


    # Checks if samples have been dropped and replaces 0.0 with next value
    def check_for_zero(self, PSD):
        try:
            index = list(PSD).index(0.0)
            print('Dropped sample was recovered!')
            PSD[index] = (PSD[index+1]+PSD[index-1])/2
            return PSD
        except:
            return PSD


