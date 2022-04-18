from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, Galactic

class Coordinates:
    
    # init function creates pyephem observer and stores it in self
    def __init__(self, lat, lon):
        self.QTH = EarthLocation(lat = lat*u.degree, lon=lon*u.degree,height=0*u.m)
        self.TIME = Time.now()
    

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


    # Calculates observers velocity to the observed area relative to the barycenter for Earth and the Sun
    def radialVelocityCorrection(self, alt, az):
        horizontal_coord = AltAz(alt = alt*u.degree, az = az*u.degree, pressure = 0*u.bar, obstime = self.TIME,location=self.QTH)
        eq_coord = SkyCoord(horizontal_coord.transform_to(ICRS()))

        v_observer = eq_coord.radial_velocity_correction(kind='barycentric', obstime=self.TIME, location=self.QTH)
        v_observer = -v_observer.to(u.km/u.s)

        return round(v_observer.value, 2)
