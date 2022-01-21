from kivy.config import Config
Config.set('graphics', 'resizable', 0)

import os
import pyperclip
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder


class PyLineSDR(MDApp):
    def build(self):
        self.host = False
        self.client = False

        Window.size = (1000, 500)
        return Builder.load_file("src/ui.kv")

    
    # Change booleans for RTL-TCP streaming
    def checkboxChecked(self, instance, label, value):
        if label == "host":
            self.host = value
        elif label == "client":
            self.client = value
    
    # Generate a command from the supplied parameters
    def getCommand(self):
        self.sample_rate = self.root.ids.sample_rate.text if self.root.ids.sample_rate.text is not "" else 2400000
        self.fft_res = self.root.ids.fft_res.text if self.root.ids.fft_res.text is not "" else 11
        self.ppm_offset = self.root.ids.ppm_offset.text if self.root.ids.ppm_offset.text is not "" else 0
        self.fft_num = self.root.ids.fft_num.text if self.root.ids.fft_num.text is not "" else 1000

        self.latitude = self.root.ids.latitude.text if self.root.ids.latitude.text is not "" else 0
        self.longitude = self.root.ids.longitude.text if self.root.ids.longitude.text is not "" else 0
        self.azimuth = self.root.ids.azimuth.text if self.root.ids.azimuth.text is not "" else 0
        self.altitude = self.root.ids.altitude.text if self.root.ids.altitude.text is not "" else 0

        self.client_ip = self.root.ids.client_ip.text if self.root.ids.client_ip.text is not "" else "none"

        self.median = self.root.ids.median.text if self.root.ids.median.text is not "" else 3
        self.degree_interval = self.root.ids.degree_interval.text if self.root.ids.degree_interval.text is not "" else 0

        command_prefix = "py H-line.py" if os.name == "nt" else "python3 H-line.py"

        if self.client is True:
            command = f"{command_prefix} -s {self.sample_rate} -r {self.fft_res} -n {self.fft_num} -l {self.latitude} -g {self.longitude} -z {self.azimuth} -a {self.altitude} -e {self.client_ip} -m {self.median} -i {self.degree_interval}"
        elif self.host is True:
            command = f"{command_prefix} -s {self.sample_rate} -r {self.fft_res} -n {self.fft_num} -l {self.latitude} -g {self.longitude} -z {self.azimuth} -a {self.altitude} -t -m {self.median} -i {self.degree_interval}"
        else:
            command = f"{command_prefix} -s {self.sample_rate} -r {self.fft_res} -n {self.fft_num} -l {self.latitude} -g {self.longitude} -z {self.azimuth} -a {self.altitude} -m {self.median} -i {self.degree_interval}"

        # Update label text
        self.root.ids.command.text = command
    
    def copyCommand(self):
        command = self.root.ids.command.text
        pyperclip.copy(command)
        print(f"Command copied! {command}")
    
    def runObservation(self):
        print("Starting observation!")
        os.system(self.root.ids.command.text)

if __name__ == "__main__":
    PyLineSDR().run()
