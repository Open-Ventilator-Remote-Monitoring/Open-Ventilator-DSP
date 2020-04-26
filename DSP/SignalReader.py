import pyaudio
import sounddevice as sd
import numpy as np

"""
There's a ton of unused code in here. There are basically two ways to read an audio device:
1. Set up a callback function to be called periodically by the sounddevice object.
2. Manually read a buffer from the sounddevice audio stream.

This signal reader is set up to be able to manually read the audio stream, but in the current
implementation I am using a callback inside OpenMonitorDSPProcess so this class is basically only used
for setting up and containing the audio stream.

"""
class SignalReader(object):
    def __init__(self, audio_callback):
        self.desired_sampling_rate = 40000
        self.max_sample_rate = 384000
        self.supported_devices = ["Microphone (USB PnP Sound Devic"] #This is misspelled on purpose, the sounddevice library actually reports this name.
        self.audio_stream_datatype = pyaudio.paInt16
        self.audio_stream = None
        self.sampling_rate = self.max_sample_rate
        self.device_id = -1
        self.buffer = []
        self.audio_callback = audio_callback

    def read(self, num, oversample_num = 1):
        print()
        del self.buffer
        self.audio_stream.start()
        self.buffer, flag = self.audio_stream.read(num)
        self.audio_stream.stop()

        print("SAMPLED {} DATA POINTS\n"
              "OVERSAMPLED {} TIMES\n"
              "SAMPLING RATE: {}".format(len(self.buffer),
                                         oversample_num,
                                         self.sampling_rate))

        if oversample_num > 1:
            return self.oversample_and_average(self.buffer, oversample_num)

        return self.buffer

    def oversample_and_average(self,audio,num):
        averaged = []
        for i in range(0,len(audio)-num,num):
            averaged.append(sum(audio[i:i+num])/num)
        return averaged

    def setup(self):
        device_id = self.find_device_id()
        print("DEVICE ID =",device_id)
        self.device_id = device_id

        assert self.device_id != -1, "!OPEN MONITOR DSP PROCESS UNABLE TO FIND SUPPORTED MICROPHONE!"

        rate = self.find_max_supported_sample_rate()
        self.sampling_rate = 40000 #set this to rate if you want to enable oversampling/averaging (this currently does not work).
        print("SETTING SAMPLING RATE TO",self.sampling_rate)

        self.audio_stream = sd.InputStream(
            device=self.device_id, channels=1,
            samplerate=self.sampling_rate, callback=self.audio_callback)

    def find_device_id(self):
        x = sd.query_devices()

        idx = 0
        for arg in x:
            print(arg["name"])
            if arg["name"] in self.supported_devices:
                return idx
            idx += 1
        return -1

    def find_max_supported_sample_rate(self):
        for i in range(self.max_sample_rate, 0, -1000):
            print(i)
            try:
                stream = sd.InputStream(
                    device=self.device_id, channels=1,
                    samplerate=i, callback=None)
                stream.stop()
                factor = i / self.desired_sampling_rate
                return int(factor)*self.desired_sampling_rate
            except Exception as e:
                print(e)
                continue

        return -1

    def cleanup(self):
        self.audio_stream.stop()
        del self.audio_stream
        self.audio_stream = None