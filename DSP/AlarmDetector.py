import numpy as np
from Util import RunningStats

"""
This class keeps track of the power in the filtered audio signal and sets the status of the detected alarm.

"""
class AlarmDetector(object):
    def __init__(self, sampling_rate=40000, std_update_rate=2000, alarm_detection_threshold=1.5):
        self.alarm_detection_threshold = alarm_detection_threshold
        self.ticks_per_reset = std_update_rate
        self.rate = sampling_rate
        self.stdev_history = []
        self.total_ticks = 0
        self.current_std = 0
        self.ticks = 0
        self.alarm = False

        self.stats = RunningStats.PowerStat()

    def tick(self, signal):
        self.ticks+=1
        self.total_ticks += 1
        self.update_signal_reading(signal)
        if self.ticks > self.ticks_per_reset:
            self.check_alarm()
            self.stats.reset()

    def update_signal_reading(self, signal):
        self.stats.increment(signal)

    def check_alarm(self):
        """
        The idea is as follows:
        1. Compute the power in the most recent slice of the signal
        2. check for a spike in power
        3. Enable the alarm when a spike upward is detected
        4. Disable the alarm if it is already on and a spike downward is detected

        This is implemented in the following way:
        The current power is measured as the standard deviation of the signal over the most recent slice (of length std_update_rate).
        The stdev is accumulated with a running statistic to save compute time. Note that right now I am computing power
        by accumulating x*X every tick to test how well that works. This may or may not be what I use in the final product.
        Every std_update_rate ticks, the accumulated power is compared to the mean value of all power values which have been
        accumulated since the last time the state of the alarm changed. If the current power passes a threshold when compared
        to that mean value, we decide to change the state of the alarm.

        Some thoughts:
        I really don't like the use of a user-defined threshold here, I wonder if there is some way to establish a
        baseline signal power level automatically. I'm not sure if accumulating power as x*x or as the stdev of the
        signal over time is better.
        :return:
        """

        self.ticks = 0
        thresh = self.alarm_detection_threshold

        std = self.stats.std
        print("Signal power:",std)
        self.stdev_history.append(std)
        if len(self.stdev_history) < 3 or self.total_ticks < self.rate / 2:
            return

        if not self.alarm and std >= np.mean(self.stdev_history) * thresh:
            print("ALARM DETECTED")
            self.alarm = True
            self.stdev_history = []

        elif self.alarm and std <= np.mean(self.stdev_history) / thresh:
            print("ALARM TURNED OFF")
            self.alarm = False
            self.stdev_history = []

    def get_alarm_status(self):
        return self.alarm