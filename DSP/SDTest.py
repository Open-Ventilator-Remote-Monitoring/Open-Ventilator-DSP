import sounddevice as sd
import numpy as np
import time
from Util import Grapher as graph
class test(object):
    def __init__(self):
        self.buffer = []
        self.stream = []
        self.t = time.time()
        self.tick = 0

    def start(self):
        supported = ["Microphone (USB PnP Sound Devic","Microphone (Blue Snowball)"]
        x = sd.query_devices()

        idx = 0
        for arg in x:
            print(arg["name"])
            if arg["name"] in supported:
                break
            idx += 1

        stream = sd.InputStream(
            device=idx, channels=1,
            samplerate=40000, callback=None)
        stream.start()
        print(stream.read(100))
        stream.stop()
        # with stream:
        #     while True:
        #         continue

    def callback(self, indata, frames, timestamp, status):

        if time.time() - self.t >= 1:
            print(len(self.buffer), (time.time()-self.t))
            graph.plot_data(self.buffer)
            graph.save_plot("test_{}.png".format(self.tick))
            self.tick += 1
            self.buffer = []
            self.t = time.time()
        for arg in indata:
            self.buffer.append(arg)
