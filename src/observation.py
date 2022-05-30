import json

# Import necessary classes/modules
from rtl import RTL
from plot import Plotter
from ephem import Coordinates as coords
from dsp import DSP as dsp
from analysis import Analysis

class Observation:
    # Initialize observation with corresponding parameters
    def __init__(self, **kwargs):
        self.ONE_DAY_OBSERVING = kwargs["24h"]
        self.DEG_INTERVAL = kwargs["degree_interval"]
        self.DATAFILE = kwargs["datafile"]
    

    # Get's the wanted SDR or runs a host
    def getSDR(self, **param):
        SDR = RTL(sample_rate = param["sample_rate"], PPM_offset = param["PPM_offset"], host_IP = param["host_IP"])
        # Host server
        if param["TCP_host"]:
            SDR.tcpHost()
            quit()
        
        # Get SDR
        if param["connect_to_host"]:
            sdr = SDR.rtlTcpClient()
        else:
            sdr = SDR.rtlClient()
        
        return sdr


    # Calculates RA and dec coordinates for the observation
    # Stores the galactic coordinates too for later
    def getCoordinates(self, current_time, **coordinates):
        lat, lon = coordinates['latitude'], coordinates['longitude']
        alt, az = coordinates['altitude'], coordinates['azimuth']
        elevation = coordinates['elevation']
        self.time = current_time

        # Instantiate an observer
        Coordinates = coords(lat, lon, elevation, current_time)
        self.RA, self.DEC = Coordinates.equatorial(alt, az)
        self.GAL_LON, self.GAL_LAT = Coordinates.galactic(alt, az)

        return Coordinates
    

    # Collects data from a given SDR
    def collectData(self, sdr, sample_rate, **dsp_param):
        # Returns the final processed data
        DSP = dsp(resolution = dsp_param["resolution"], num_fft = dsp_param["number_of_fft"], median = dsp_param["median"])
        
        # Now, collect data
        sdr.center_freq = 1420405750
        self.freqs = DSP.generateFreqs(sample_rate = sample_rate)
        self.h_line_data = DSP.sample(sdr)
        
        # Sample blank
        sdr.center_freq += 3200000
        self.blank_data = DSP.sample(sdr)

        # Get SNR spectrum, correct for slant and apply median filter
        SNR_spectrum = DSP.combineSpectrums(freqs = self.freqs, h_line_data = self.h_line_data, blank_data = self.blank_data)
        self.SNR_spectrum = DSP.correctSlant(SNR_spectrum)
        if dsp_param["median"] != 0:
            self.SNR_spectrum = DSP.applyMedian(self.SNR_spectrum)

    
    # Gets the radial velocity, LSR correction, max SNR and etc
    def analyzeData(self, coord_class):
        ANALYSIS_CLASS = Analysis()
        # Get radial velocity and maximum SNR
        self.max_SNR, self.observed_radial_velocity = ANALYSIS_CLASS.getRadialVelocity(self.SNR_spectrum, self.freqs)

        # Get frequency corrections w.r.t. barycenter and Local Standard of Rest
        self.barycenter_vel_correction = coord_class.barycenterVelocityCorrection(self.RA, self.DEC)
        vel_wrt_barycenter = self.observed_radial_velocity + self.barycenter_vel_correction
        self.lsr_vel_correction = coord_class.lsrVelocityCorrection(self.RA, self.DEC, vel_wrt_barycenter)
        self.corrected_radial_vel = vel_wrt_barycenter + self.lsr_vel_correction


    # Plot the data
    def plotData(self, **params):
        PLOT = Plotter(params["plot_map"], params["y_min"], params["y_max"])

        plot_info = {
            "ra": self.RA,
            "dec": self.DEC,
            "gal_lon": self.GAL_LON,
            "gal_lat": self.GAL_LAT,
            "barycenter_correction": self.barycenter_vel_correction,
            "lsr_correction": self.lsr_vel_correction,
            "SNR": self.max_SNR,
            "observed_radial_velocity": self.observed_radial_velocity
        }
        PLOT.plot(self.freqs,self.SNR_spectrum,**plot_info)


    # Writes a datafile with all the collected data from the observation
    def writeDatafile(self, **kwargs):
        # kwargs = SDR, DSP, observer and observation parameters
        json_file = {
            "Observation parameters": kwargs,
            "Observation results": {
                "Time": str(self.time),
                "RA": self.RA,
                "Dec": self.DEC,
                "Galactic lon": self.GAL_LON,
                "Galactic lat": self.GAL_LAT,
                "Observed radial velocity": self.observed_radial_velocity,
                "Barycenter correction": self.barycenter_vel_correction,
                "LSR correction": self.lsr_vel_correction,
                "Radial velocity": self.corrected_radial_vel,
                "Max SNR": self.max_SNR
            },
            "Data": {
                "Blank spectrum": self.blank_data.tolist(),
                "H-line spectrum": self.h_line_data.tolist(),
                "SNR Spectrum": self.SNR_spectrum.tolist(),
                "Frequency list": self.freqs.tolist()
            }
        }

        # Save file
        with open(f"Spectrums/data(ra={self.RA},dec={self.DEC}).json", "w") as file:
            json.dump(json_file, file, indent = 4)
            


        