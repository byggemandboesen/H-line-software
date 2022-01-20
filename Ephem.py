import ephem
from ephem import degree
import numpy as np

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
    def equatorial(self, num, interval):
        ra, dec = self.QTH.radec_of(str(self.az), str(self.alt))

        # Create list of RA coordinates for 24H observing feature
        if interval == 0:
            return round(ra / degree, 1), round(dec / degree, 1)
        else:
            ra_list = [round(ra / degree, 1)]

            # We don't want the RA > 360 hence the if statements below
            for i in range(1, int(num)):
                ra_list.append(round(ra_list[i-1] + interval if ra_list[i-1] + interval <= 360.0 else interval - (360.0 - ra_list[i-1]), 1))

            return ra_list, round(dec / degree, 1)


    # Calculates apparent velocity of galactic coordinate
    def observer_velocity(self, lat, lon):
        orb_vel = 220 # km/s
        # Radian stuff
        lat = lat * np.pi / 180
        lon = lon * np.pi / 180

        # We determine the angle bewteen Earth's velocity-vector and a unit-vector to the galactic coordinate
        obj_vec = np.array(
            [1 * np.cos(lon) * np.cos(lat),
            1 * np.sin(lon) * np.cos(lat),
            1 * np.sin(lat)])
        sun_vec = np.array([0, orb_vel, 0])

        dot_prod = np.dot(obj_vec, sun_vec)
        angle = np.arccos(dot_prod/(np.linalg.norm(obj_vec)*np.linalg.norm(sun_vec)))
        
        # Multiply solar system orbit velocity with cos to the angle to the object to find velocity component in that direction
        rel_vel = orb_vel * np.cos(angle)
        return rel_vel
