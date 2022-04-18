import numpy as np
import matplotlib.pyplot as plt

class DSP():
    def __init__(self, **kwargs):
        self.FFT_SIZE = 2**kwargs["resolution"]
        self.NUM_FFT = kwargs["number_of_fft"]
        self.MEDIAN = kwargs["median"]
    
    
    # This samples from a given SDR
    def sample(self, sdr):
        # Create array for summing FFTs
        PSD_sum = np.zeros(self.FFT_SIZE)
        
        for i in range(self.NUM_FFT):
            samples = np.array(sdr.read_samples(self.FFT_SIZE))
            PSD = (np.abs(np.fft.fft(samples))/self.FFT_SIZE)**2
            PSD_zero_checked = self.checkForZero(PSD)
            PSD_log = 10.0*np.log10(PSD_zero_checked)

            PSD_sum = np.add(PSD_sum,np.fft.fftshift(PSD_log))
        
        mean_PSD = np.true_divide(PSD_sum,self.NUM_FFT)
        return mean_PSD


    # Return SNR spectrum together with highest H-line SNR
    def combineSpectrums(self, freqs, h_line_data, blank_data):
        diff = np.subtract(h_line_data, blank_data)

        # The above spectrum may not be at 0.0 SNR.
        # To fix this, we shift the spectrum to 0.0
        # The distance to shift is equal to the noise floors mean (ie. area around H-line, hence the slicing below)
        min_index = (np.abs(np.array(freqs)-1419750000)).argmin()
        max_index = (np.abs(np.array(freqs)-1421200000)).argmin()
        sliced = np.concatenate((diff[:min_index], diff[max_index:]))
        noise_floor = np.true_divide(np.sum(sliced),len(sliced))
        shifted_SNR = diff-noise_floor
        slant_corrected = self.correctSlant(shifted_SNR)

        return slant_corrected
    
    # Apply median filter to data
    def applyMedian(self,data):
        for i in range(len(data)):
            data[i] = np.mean(data[i:i+self.MEDIAN])
        return data

    
    # Correct for slanted data
    def correctSlant(self, data):
        X = np.linspace(0,len(data) - 1, len(data))
        slope, intersect = np.polyfit(X, data, 1)
        data = np.array([data[i] - (intersect + i * slope) for i in range(len(X))])
        return data

    
    # Checks if samples have been dropped and replaces 0.0 with average of value before and after
    def checkForZero(self, PSD):
        index = np.array(np.where(PSD == 0))
        if index.size == 0:
            return PSD
        print('Dropped sample was recovered!')
        PSD[index] = np.mean(PSD[index+1]+PSD[index-1])
        return PSD

    # Returns numpy array of frequencies for a given sample rate and resolution
    def generateFreqs(self,sample_rate):
        start_freq = 1420405750 - sample_rate/2
        stop_freq = 1420405750 + sample_rate/2
        freqs = np.linspace(start = start_freq, stop = stop_freq, num = self.FFT_SIZE)
        return freqs
    
