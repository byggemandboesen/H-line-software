from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, SpectralCoord, EarthLocation, AltAz, ICRS, Galactic

# Suppress warnings
import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

# Import some helping functions
from dsp import ANALYSIS

class Coordinates:
    
    # init function creates pyephem observer and stores it in self
    def __init__(self, lat, lon, time):
        self.QTH = EarthLocation(lat = lat*u.degree, lon=lon*u.degree,height=0*u.m)
        self.TIME = Time(time)
    

    # Returns galactic coordinates
    def galactic(self, alt, az):
        horizontal_coord = AltAz(alt = alt*u.degree, az = az*u.degree, pressure = 0*u.bar, obstime = self.TIME,location=self.QTH)
        gal_coord = horizontal_coord.transform_to(Galactic())

        # Return lon (l), lat (b)
        return round(gal_coord.l.degree, 2), round(gal_coord.b.degree, 2)
    

    # Returns equatorial coordinates
    def equatorial(self, alt, az):
        horizontal_coord = AltAz(alt = alt*u.degree, az = az*u.degree, pressure = 0*u.bar, obstime = self.TIME,location=self.QTH)
        eq_coord = SkyCoord(horizontal_coord.transform_to(ICRS()))

        return round(eq_coord.ra.degree, 2), round(eq_coord.dec.degree, 2)


    # Calculates the velocity correction to the observed area with respect to the barycenter for Earth and the Sun
    def barycenterVelocityCorrection(self, ra, dec):
        # Create coordinate to target in equatorial coordinates
        eq_coord = SkyCoord(ra = ra*u.degree, dec = dec*u.degree, frame = 'icrs')

        # Calculate radial velocity correction w.r.t. the barycenter
        v_observer = eq_coord.radial_velocity_correction(kind='barycentric', obstime=self.TIME, location=self.QTH)
        v_observer = v_observer.to(u.km/u.s)

        return round(v_observer.value, 2)
    

    # Calculate velocity correction with respect to Local Standard of Rest
    def lsrVelocityCorrection(self, ra, dec, radial_vel_wrt_barycenter):
        # Define target coordinate in equatorial coordinates
        eq_coord = SkyCoord(ra = ra*u.degree, dec = dec*u.degree, frame = 'icrs')
        # Define observer and its position
        observer_loc = self.QTH.get_itrs(self.TIME)
        
        # Create SpectralCoord from observer location, target and the observed frequency of the target
        spectral_coord = SpectralCoord(ANALYSIS.freqFromRadialVel(radial_vel_wrt_barycenter)*u.Hz, observer=observer_loc,target=eq_coord)
        
        # Calculate what the observed frequency would be w.r.t. the Local Standard of Rest
        freq_wrt_lsrk = spectral_coord.with_observer_stationary_relative_to("lsr")
        
        # Calculate the correction in radial velocity
        correction = ANALYSIS.radialVelFromFreq(freq_wrt_lsrk.value) - radial_vel_wrt_barycenter
        
        return round(correction, 2)
        
