from statistics import mean
import numpy as np
import matplotlib.pyplot as plt

from analysis import Analysis
ANALYSIS = Analysis()

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
        min_index = (np.abs(np.array(freqs)-ANALYSIS.freqFromRadialVel(120))).argmin()
        max_index = (np.abs(np.array(freqs)-ANALYSIS.freqFromRadialVel(-120))).argmin()
        sliced = np.concatenate((diff[:min_index], diff[max_index:]))
        shifted_SNR = diff-np.mean(sliced)

        return shifted_SNR

    
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
    

    # Remove large noise spikes
    def removeSpikes(self, data):
        # Look for differences in SNR between bin that are largely greater than two standard deviations
        mean = np.mean(data)
        std = np.std(data)
        
        # Get indices of start/end of noise spikes
        up_indices = []
        down_indices = []
        diff = np.array([data[i+1]-data[i] for i in range(len(data)-1)])
        diff_std = np.std(diff)
        
        # Iterate over each bin to identify large changes in SNR
        for i in range(len(data)-1):
            diff[i] = data[i+1]-data[i]
            if data[i+1]-data[i] > 5*diff_std:
                up_indices.append(i)
            elif data[i+1]-data[i] < - 5*diff_std:
                down_indices.append(i)

        X_up = [up for up in up_indices]
        X_down = [down for down in down_indices]

        Y_up = [diff[up] for up in up_indices]
        Y_down = [diff[down] for down in down_indices]
        plt.plot(X_up,Y_up,marker='o',color='b',label="UP")
        plt.plot(X_down,Y_down,marker='o',color='g',label="DOWN")
        plt.plot(diff,label="diff")
        #plt.plot(data,color='r',label="Data")
        plt.axhline(2*diff_std,label="STD")
        plt.legend()
        #plt.ylim(-0.2,1.3)
        plt.show()

        # Next, replace noise spikes
        # Spikes are replaced with random values around the median, which then have 1% gaussian noise applied
        for i in range(0,len(up_indices),2):
            num_points = down_indices[i]-up_indices[i]+20
            noise = np.random.normal(0,std,num_points)*0.05
            # data[up_indices[i]-5:down_indices[i]+5] = np.add(rands, noise)
            data[up_indices[i]-10:down_indices[i]+10] -= np.add(data[up_indices[i]-10:down_indices[i]+10],noise)

        return data
