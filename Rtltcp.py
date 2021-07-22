import socket
from rtlsdr import RtlSdrTcpServer
from rtlsdr.rtlsdrtcp.client import RtlSdrTcpClient

from Receive import Receiver

# For RTL-TCP
class RTLTCP:

    def __init__(self, sample_rate, ppm, resolution, num_FFT, num_med):

        self.sample_rate = sample_rate
        
        self.ppm = ppm
        if ppm != 0:
            self.freq_correction = ppm
        self.gain = 'auto'

        self.resolution = resolution
        self.num_FFT = num_FFT
        self.num_med = num_med

    # Host for RTL-TCP streaming
    def rtltcphost(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            server = RtlSdrTcpServer(hostname = local_ip, port = 5050)
            print('Starting SDR - Waiting for client (Kill with ctrl + C)')
            server.run_forever()
        except Exception as err:
            print(f'Type = {type(err)} occured with message = {err}')
            quit()

    # Client for RTL-TCP streaming
    def rtltcpclient(self, ip):
        
        # Try to init a client connection with settings
        try:
            client = RtlSdrTcpClient(hostname = ip, port = 5050)
            
            client.center_freq = 1420405000
            client.sample_rate = self.sample_rate

            Receiver_class = Receiver(TCP = True, client = client,sample_rate = self.sample_rate, ppm = self.ppm, resolution = self.resolution, num_FFT = self.num_FFT, num_med = self.num_med)
            freqs, data = Receiver_class.receive()

            return freqs, data    

        except Exception as err:
            print(f'Type = {type(err)} occured with message = {err}')
            quit()