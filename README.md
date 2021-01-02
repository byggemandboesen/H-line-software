# H-line-software
This software is created with the main purpose of receiving the hydrogen line at a frequency of approximately 1420.4MHz. <br>
The software uses the [pyrtlsdr library](https://github.com/roger-/pyrtlsdr) to collect samples from the RTL-SDR V3.0 dongle and numpy to perform FFT and signal processing. Finally, the data is shown in a chart from the pyplot library in matplotlib.

## Installing
As usual, the code should be downloaded with git clone.
~~~
git clone https://github.com/byggemandboesen/H-line-software.git
~~~
Some packages are required which can be downloaded with pip (requirements.txt will be added):
~~~
pip install matplotlib
pip install numpy
pip install pyrtlsdr
~~~

## Usage
The software is meant for observing the hydrogen line but it also allows to plot any other frequency inside the RTL-SDR tuner ranger. This means the software has set default preferences for the hydrogen line, but these can be modified according with argparser according to your preferences. <br>
The following parameters can be modified:
~~~
optional arguments:
  -h, --help          show this help message and exit
  -f Frequency        Center tuning frequency in Hz
  -s Sample rate      Tuner sample rate
  -o PPM offset       Set custom tuner offset PPM
  -r Resolution       Amount of samples = 2 raised to the power of the input
  -n Number of FFT's  Number of FFT's to be collected and averaged
  -z Azimuth          The azimuth of the antenna as a float, north is positive
  -e Elevation        The elevation of the antenna as a float, east is positive
~~~
The azimuth and elevation don't play a role yet, since this will be used in the future for mapping the Milky Way

### TODO
* Direct bias-t interaction
* Determine signal to noise ratio(SNR)
* Write SNR and observed doppler to file with galactic coordinates from dish direction and time
