import numpy as np
class SignalGenerator(object):
    def __init__(self, signal_list):
        self.t = 0
        self.snr = 0
        self.freq = 0
        self.amplitude = 0
        self.offset = 0

        self.signals = signal_list
        self.current_signal_key = -1
        self.next_signal()

    def next_signal(self):
        self.current_signal_key += 1
        if self.current_signal_key >= len(self.signals):
            self.current_signal_key = 0

        self.t = 0
        sig = self.signals[self.current_signal_key]
        self.amplitude = sig["amplitude"]
        self.freq = sig["frequency_hz"]
        self.offset = sig["offset_amplitude"]
        self.snr = np.power(10, sig["snr_db"] / 10)

    def sample(self):
        noise = np.random.randn(1)[0]
        sig = np.sin(self.t*self.freq*2*np.pi)*self.amplitude + self.offset

        sum1 = sig*sig
        sum2 = noise*noise

        if sum2 == 0 or sum1 == 0:
            return sig + noise

        snr = sum1/sum2
        factor = snr / self.snr
        noise = noise * np.sqrt(factor)

        return noise + sig

    def sample_over_time(self, num_sec, num_oversamples, sampling_rate):
        num_samples = num_sec * sampling_rate
        time_increment = num_sec / (num_samples * num_oversamples)
        signal = []

        for i in range(int(num_samples)+1):
            if self.t >= self.signals[self.current_signal_key]["duration_sec"]:
                self.next_signal()

            x = 0
            for j in range(num_oversamples):
                self.t += time_increment
                x += self.sample()
            signal.append(x / num_oversamples)
        return signal