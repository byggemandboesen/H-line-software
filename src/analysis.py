import astropy.units as u
import numpy as np

# Analyze data, eg. find/calculate radial velocity, SNR and etc.
class Analysis():
    def __init__(self):
        # Constants
        self.H_FREQUENCY = 1420405750
        self.C_SPEED = 299792.458 # km/s
    
    
    # Returns the radial velocity and maximum SNR
    def getRadialVelocity(self, data, freqs):
        # Center around H-line
        # TODO Change to radial velocity instead of frequency
        min_index = (np.abs(np.array(freqs)-self.freqFromRadialVel(120))).argmin()
        max_index = (np.abs(np.array(freqs)-self.freqFromRadialVel(-120))).argmin()

        SNR = np.amax(data[min_index:max_index])
        #Get index of max SNR
        index = np.where(data==SNR)[0][0]
        radial_vel = self.radialVelFromFreq(freqs[index])

        return np.round(SNR, 2), np.round(radial_vel, 2)
    

    # Returns radial velocity from frequency
    def radialVelFromFreq(self, freq):
        H_freq = u.doppler_radio(self.H_FREQUENCY*u.Hz)
        measured = freq*u.Hz
        v_doppler = measured.to(u.km/u.s,equivalencies=H_freq)
        
        return v_doppler.value
    

    # Returns frequency from radial velocity
    def freqFromRadialVel(self, radial_vel):
        H_freq = u.doppler_radio(self.H_FREQUENCY*u.Hz)
        measured = radial_vel*u.km/u.s
        freq = measured.to(u.Hz,equivalencies=H_freq)
        
        return freq.value
    

    #TODO Gaussian curve modelling??