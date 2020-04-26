from MPFramework import MPFProcess
from DSP import IIRFilter, AlarmDetector, SignalReader
import time
import numpy as np
from Util import Grapher as graph

"""
This class does the bulk of the work. It is a new process running in its own python instance. Here we
set up everything, read the audio stream, filter the incoming signal, and report the status of the alarm.
Refer to the MPFProcess class for the way the functions in this class are called.
"""
class OpenMonitorDSPProcess(MPFProcess):
    UPDATE_CONFIG_HEADER = "OpenMonitorDSP_Update_config"
    ALARM_STATUS_HEADER = "OpenMonitorDSP_Alarm_Status"

    def __init__(self, process_name = "OpenMonitorDSP_Process", loop_wait_period=None):
        super().__init__(process_name=process_name, loop_wait_period=loop_wait_period)
        self.cfg = None
        self.high_pass_filter = None
        self.low_pass_filter = None
        self.alarm_detector = None
        self.signal_reader = None
        self.oversample_amount = 1
        self.num = 0
        self.alarm = []
        self.signal = []

    def init(self):
        self.task_checker.wait_for_initialization(OpenMonitorDSPProcess.UPDATE_CONFIG_HEADER)
        self.cfg = self.task_checker.latest_data
        self.configure()
        self.t = time.time()

    def update(self, header, data):
        if header == OpenMonitorDSPProcess.UPDATE_CONFIG_HEADER:
            self.cfg.clear()
            self.cfg = data
            self.configure()

    def step(self):
        #This gets called on a loop until the process is closed.
        self.signal_reader.audio_stream.start()
        self.t = time.time()
        while time.time() - self.t < self.cfg["alarm_report_period"]:
            continue
        self.signal_reader.audio_stream.stop()

    def publish(self):
        #This gets called after step() on a loop.
        self.results_publisher.publish(data=self.alarm_detector.get_alarm_status(),
                                       header=OpenMonitorDSPProcess.ALARM_STATUS_HEADER)


        if len(self.signal) >= self.cfg["sampling_rate"]:
            #Plot the data we just recorded and save it to data/graphs/graph_test_{num}.png
            print("saving")
            graph.plot_data(self.signal)
            graph.plot_data(np.multiply(self.alarm, np.max(self.signal)),clear=False)
            graph.save_plot("test_{}.png".format(self.num))
            print("saved")

            self.num+=1
            self.signal = []
            self.alarm = []

    def audio_callback(self, indata, frames, timestamp, status):
        #This is the callback to be used by the sounddevice audio stream.
        t1 = time.time()

        # We use this to normalize the amplitude of the incoming signal. We can do this because our band-pass filter will
        # reduce the energy of everything outside our desired frequency bands after this happens.
        max_val = 1
        max_in = np.max(indata)
        if max_in != 0:
            max_val = max_in


        for i in range(0, len(indata)):
            low_pass = self.low_pass_filter.filter(indata[i]/max_val)
            band_pass = self.high_pass_filter.filter(low_pass)

            self.alarm_detector.tick(band_pass)
            self.signal.append(band_pass)
            self.alarm.append(self.alarm_detector.get_alarm_status())

        print("Processing time per sample:",(time.time()-t1)/len(indata))

    def cleanup(self):
        self.cfg.clear()
        if self.signal_reader is not None:
            self.signal_reader.cleanup()

    def configure(self):
        self.high_pass_filter = IIRFilter(self.cfg["high_pass_coeffs"])
        self.low_pass_filter = IIRFilter(self.cfg["low_pass_coeffs"])
        self.alarm_detector = AlarmDetector(
            sampling_rate=self.cfg["sampling_rate"],
            std_update_rate=self.cfg["std_update_rate"],
            alarm_detection_threshold=self.cfg["alarm_detection_threshold"])
        self.signal_reader = SignalReader(self.audio_callback)
        self.signal_reader.setup()
        self.oversample_amount = self.signal_reader.sampling_rate//self.cfg["sampling_rate"]