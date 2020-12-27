import os
import operator
import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt

# Receives data and returns averaged IF values as two tuples.
def receive(frequency, sample_rate, ppm, resolution, num_FFT):
    sdr = RtlSdr()

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

    # configure SDR
    sdr.sample_rate = sample_rate
    sdr.center_freq = frequency
    # Somehow the SDR doesn't want to set the offset PPM to 0 so we avoid that
    if ppm is not 0: 
        sdr.freq_correction = ppm
    sdr.gain = 'auto'
    sample_resolution = 2**resolution

    # While loop receives data in specified period of time
    print(f'Reading {num_FFT} different FFT\'s...')
    counter = 0.0
    PSD_summed = (0, )* sample_resolution
    while (counter <= num_FFT):
        samples = sdr.read_samples(sample_resolution)
        
        # Perform FFT and PSD-analysis
        PSD = np.abs(np.fft.fft(samples)/sdr.sample_rate)**2
        PSD_log = 10*np.log10(PSD)
        PSD_summed = tuple(map(operator.add, PSD_summed, np.fft.fftshift(PSD_log)))

        counter += 1.0

    print('Averaging FFT\'s...')
    averaged_PSD = tuple(sample/counter for sample in PSD_summed)

    # Get observed frequency range and plots PSD points
    print('Plotting PSD-points...')
    PSD_freqs = np.linspace(start = sdr.center_freq - sdr.sample_rate/2, stop = sdr.center_freq + sdr.sample_rate/2, num = sample_resolution)
    plt.plot(PSD_freqs, averaged_PSD)
    plt.grid()
    plt.xlabel('Frequency / MHz')
    plt.ylabel('Relative power / dB')

    path = f'D:/Documents/Programming/H-line-software/fft-{sample_resolution}-{num_FFT}.png'
    plt.savefig(path, dpi = 300)

    # Show image
    # os.system(path)

    # Close the SDR
    sdr.close()


