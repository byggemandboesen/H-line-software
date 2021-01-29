import ephem
from ephem import degree

class Coordinates:
    
    # init function creates pyephem observer and stores it in self
    def __init__(self, lat, lon, alt, az):
        self.QTH = ephem.Observer()
        self.QTH.lat = str(lat)
        self.QTH.lon = str(lon)
        self.QTH.pressure = 0
        self.alt = alt
        self.az = az
    
    # Returns galactic coordinates
    def galactic(self):
        ra, dec = self.QTH.radec_of(str(self.az), str(self.alt))
        eq_grid = ephem.Equatorial(ra, dec)
        gal_lat, gal_lon = ephem.Galactic(eq_grid).lat / degree, ephem.Galactic(eq_grid).lon / degree

        return round(gal_lat, 1), round(gal_lon, 1)
    
    # Returns equatorial coordinates
    def equatorial(self):
        ra, dec = self.QTH.radec_of(str(self.az), str(self.alt))
        return round(ra / degree, 1), round(dec / degree, 1)

