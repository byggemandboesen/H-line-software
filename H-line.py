import numpy as np
import Receive
import argparse


# Reads user parameters and continues to read samples with chosen configurations
def main():
    parser = argparse.ArgumentParser(
        prog = 'H-line-observer',
        description = 'An interface to receive H-line data'
    )

    # Parsing options (receiver)
    parser.add_argument('-f', metavar = 'Frequency', type = int, help = 'Center tuning frequency in Hz', default = 92200000, dest = 'frequency')
    parser.add_argument('-s', metavar = 'Sample rate', type = int, help = 'Tuner sample rate', default = 1024000, dest = 'sample_rate')
    parser.add_argument('-o', metavar = 'PPM offset', type = int, help = 'Set custom tuner offset PPM', default = 0, dest = 'ppm')
    parser.add_argument('-r', metavar = 'Resolution', type = int, help = 'Amount of samples = 2 raised to the power of the input', default = 10, dest = 'resolution')
    parser.add_argument('-n', metavar = 'Number of FFT\'s', type = int, help = 'Number of FFT\'s to be collected and averaged', default = 100, dest = 'num_FFT')

    # Parsing options (observer)
    parser.add_argument('-z', metavar = 'Azimuth', type = float, help = 'The azimuth of the antenna as a float, north is positive', default = 0.0, dest = 'azimuth')
    parser.add_argument('-e', metavar = 'Elevation', type = float, help = 'The elevation of the antenna as a float, east is positive', default = 0.0, dest = 'elevation')
    
    args = parser.parse_args()

    # Receive and write data
    Receive.receive(frequency = args.frequency, sample_rate = args.sample_rate, ppm = args.ppm, resolution = args.resolution, num_FFT = args.num_FFT)

    #TODO Plot data
    


if __name__ == "__main__":
    main()
