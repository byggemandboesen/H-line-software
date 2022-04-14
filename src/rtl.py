import socket
from rtlsdr import RtlSdr
from rtlsdr import RtlSdrTcpServer
from rtlsdr.rtlsdrtcp.client import RtlSdrTcpClient

# Available sample rates
'''
3200000Hz
2800000Hz
2560000Hz
2400000Hz
2048000Hz
1920000Hz
1800000Hz
1400000Hz
1024000Hz
900001Hz
250000Hz
'''

'''
This file includes everthing controlling the RTL-SDR.
This involves TCP host and -clients and serial connections.
Each function returns a device corresponding to the wished device (host, client, serial).

The sample() function returns samples.
'''

class RTL():
    # Init with RTL parameters
    def __init__(self, **kwargs):
        self.SAMPLE_RATE = kwargs["sample_rate"]
        self.PPM_OFFSET = kwargs["PPM_offset"]
        self.CENTER_FREQ = 1420405750

        self.HOST_IP = kwargs["host_IP"]
    

    # Return a physical serial SDR client
    def rtlClient(self):
        client_sdr = RtlSdr()
        client_sdr.sample_rate = self.SAMPLE_RATE
        client_sdr.center_freq = self.CENTER_FREQ
        client_sdr.gain = 'auto'
        
        # For some reason the SDR doesn't want to set the offset PPM to 0 so we avoid that
        if self.PPM_OFFSET != 0:
                self.sdr.freq_correction = self.PPM_OFFSET
        
        return client_sdr

    # Client for RTL-TCP streaming
    # Returns a client device
    def rtlTcpClient(self):
        # Try to initiate a client connection with settings
        try:
            client_sdr = RtlSdrTcpClient(hostname = self.HOST_IP, port = 5050)
            return client_sdr
        except Exception as err:
            print(f'Type = {type(err)} occured with message = {err}')
            quit()

    # Start hosting TCP server
    def tcpHost(self):
        try:
            local_ip = self.getIp()
            print(f'Hosting server at local IP = {local_ip}')
            server = RtlSdrTcpServer(hostname = local_ip, port = 5050)
            print('Starting SDR - Waiting for client (Kill with ctrl + C)')
            server.run_forever()
        except Exception as err:
            print(f'Type = {type(err)} occured with message = {err}')
            quit()
    
    # Get ip of device
    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip_address = str(s.getsockname()[0])
        s.close()
        return ip_address
