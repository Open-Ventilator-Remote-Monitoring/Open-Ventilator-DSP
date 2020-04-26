import scipy
import numpy as np
from Util import Grapher as graph
from Util import AudioLoader, AudioProcessor, Maths
from DSP import IIRFilter, SignalGenerator, AlarmDetector, OpenMonitorDSPProcess
from MPFramework import MPFProcessHandler

"""
This file is basically my testing playground. Most of the code here either doesn't work or isn't used, I write fast 
prototypes here. This is currently the entry point of the program, and is set up to launch the DSP process and configure it.
Scroll to the bottom to find that.

"""


def setup_zoll_coeffs():
    """CHEBYSCHEV LOW-PASS 20TH ORDER IIR SOS COEFFICIENTS"""
    # CHEBY LOW, order 16, R = 1.0, 3385 BPM
    lpfg1 = 0.0205824
    lpfb1 = [1.0000000, 2.0495181, 0.9988820]
    lpfa1 = [1.0000000, -1.9027430, 0.9077117]
    lpfg2 = 0.0205824
    lpfb2 = [1.0000000, 2.4509740, 1.5129089]
    lpfa2 = [1.0000000, -1.8856149, 0.9115959]
    lpfg3 = 0.0205824
    lpfb3 = [1.0000000, 2.3140173, 1.3728307]
    lpfa3 = [1.0000000, -1.8545803, 0.9189818]
    lpfg4 = 0.0205824
    lpfb4 = [1.0000000, 2.1326239, 1.1871074]
    lpfa4 = [1.0000000, -1.8155926, 0.9295852]
    lpfg5 = 0.0205824
    lpfb5 = [1.0000000, 1.9506030, 1.0005221]
    lpfa5 = [1.0000000, -1.7756334, 0.9425651]
    lpfg6 = 0.0205824
    lpfb6 = [1.0000000, 1.7974322, 0.8433694]
    lpfa6 = [1.0000000, -1.7420169, 0.9575849]
    lpfg7 = 0.0205824
    lpfb7 = [1.0000000, 1.6858610, 0.7288571]
    lpfa7 = [1.0000000, -1.7208365, 0.9738889]
    lpfg8 = 0.0205824
    lpfb8 = [1.0000000, 1.6189705, 0.6602055]
    lpfa8 = [1.0000000, -1.7166681, 0.9911582]
    lpf = [[lpfg1, lpfa1, lpfb1], [lpfg2, lpfa2, lpfb2], [lpfg3, lpfa3, lpfb3], [lpfg4, lpfa4, lpfb4],
           [lpfg5, lpfa5, lpfb5], [lpfg6, lpfa6, lpfb6], [lpfg7, lpfa7, lpfb7], [lpfg8, lpfa8, lpfb8], ]

    # CHEBY HIhpfgH, order 20, R = 1.0, 3350 BPM
    hpfg1 = 0.5978343
    hpfb1 = [1.0000000, -2.1151119, 1.0071082]
    hpfa1 = [1.0000000, 1.0031680, 0.3718488]
    hpfg2 = 0.5978343
    hpfb2 = [1.0000000, -2.7279325, 1.8793942]
    hpfa2 = [1.0000000, 0.1526974, 0.5585491]
    hpfg3 = 0.5978343
    hpfb3 = [1.0000000, -2.5722484, 1.7181383]
    hpfa3 = [1.0000000, -0.6084834, 0.7260724]
    hpfg4 = 0.5978343
    hpfb4 = [1.0000000, -2.3475688, 1.4835743]
    hpfa4 = [1.0000000, -1.0720648, 0.8288179]
    hpfg5 = 0.5978343
    hpfb5 = [1.0000000, -1.4598861, 0.5377968]
    hpfa5 = [1.0000000, -1.3403824, 0.8892696]
    hpfg6 = 0.5978343
    hpfb6 = [1.0000000, -1.5015085, 0.5840189]
    hpfa6 = [1.0000000, -1.5003414, 0.9265625]
    hpfg7 = 0.5978343
    hpfb7 = [1.0000000, -1.5816244, 0.6711783]
    hpfa7 = [1.0000000, -1.5993642, 0.9512255]
    hpfg8 = 0.5978343
    hpfb8 = [1.0000000, -2.1037363, 1.2272155]
    hpfa8 = [1.0000000, -1.6620646, 0.9688523]
    hpfg9 = 0.5978343
    hpfb9 = [1.0000000, -1.7073865, 0.8063706]
    hpfa9 = [1.0000000, -1.7014228, 0.9825875]
    hpfg10 = 0.5978343
    hpfb10 = [1.0000000, -1.8829967, 0.9935737]
    hpfa10 = [1.0000000, -1.7243010, 0.9943778]
    hpf = [[hpfg1, hpfa1, hpfb1], [hpfg2, hpfa2, hpfb2], [hpfg3, hpfa3, hpfb3], [hpfg4, hpfa4, hpfb4],
           [hpfg5, hpfa5, hpfb5], [hpfg6, hpfa6, hpfb6], [hpfg7, hpfa7, hpfb7], [hpfg8, hpfa8, hpfb8],
           [hpfg9, hpfa9, hpfb9], [hpfg10, hpfa10, hpfb10], ]

    return [lpf, hpf]

def setup_signals(snr):
    signals = []

    signal = {}
    signal["frequency_hz"] = 3275
    signal["duration_sec"] = 1
    signal["amplitude"] = 1
    signal["offset_amplitude"] = 0
    signal["snr_db"] = snr
    signals.append(signal)

    signal = {}
    signal["frequency_hz"] = 3375
    signal["duration_sec"] = 1/2
    signal["amplitude"] = 1
    signal["offset_amplitude"] = 0
    signal["snr_db"] = snr
    signals.append(signal)

    signal = {}
    signal["frequency_hz"] = 3475
    signal["duration_sec"] = 1
    signal["amplitude"] = 1
    signal["offset_amplitude"] = 0
    signal["snr_db"] = snr
    signals.append(signal)

    return signals



def run_test(num_oversamples):
    sec = 1
    snrs = [-5]

    for snr in snrs:
        signal = SignalGenerator(setup_signals(snr))
        sampled_signal = signal.sample_over_time(sec, num_oversamples, 40000)

        graph.plot_data(sampled_signal, axis=[i for i in range(len(sampled_signal))])
        graph.save_plot("generated_signal.png", xLabel="Time", yLabel="Amplitude",
                        title="Simulated Alarm Over {:.4f} Seconds".format(sec))

        """
        lpf_filter = IIRFilter()
        hpf_filter = IIRFilter()
        final_stage_hpf = IIRFilter()

        coeffs = setup_zoll_coeffs()

        detector = AlarmDetector()

        filtered = []
        lpf = []
        hpf = []
        sig = []

        lpf_signal_slice = []
        hpf_signal_slice = []
        signal_slice = []
        
        length = 40000 / 20
        
        for entry in sampled_signal:
            filtered_low = lpf_filter.filter(entry, coeffs[0])
            #filtered_high = hpf_filter.filter(entry, coeffs[1])

            filtered_signal = final_stage_hpf.filter(filtered_low, coeffs[1])
            filtered.append(filtered_signal)

            detector.tick(filtered_signal)
            sig.append(detector.alarm)

            # lpf_signal_slice.append(filtered_low)
            # if len(lpf_signal_slice) > length:
            #     lpf_signal_slice.pop(0)
            #
            # hpf_signal_slice.append(filtered_high)
            # if len(hpf_signal_slice) > length:
            #     hpf_signal_slice.pop(0)
            #
            # signal_slice.append(filtered_signal)
            # if len(signal_slice) > length:
            #     signal_slice.pop(0)
            #
            # sig.append(np.std(signal_slice))
            # lpf.append(np.std(lpf_signal_slice))
            # hpf.append(np.std(hpf_signal_slice))

        graph.plot_data(filtered)
        # graph.plot_data(lpf, clear=False)
        # graph.plot_data(hpf, clear=False)
        graph.plot_data(sig, clear=False)
        graph.set_legend(["filtered", "alarm"])
        #graph.set_legend(["filtered", "low_pass", "high_pass", "band_pass"])
        graph.save_plot("filtered_signal_{}db_at_{} oversamples.png".format(snr, num_oversamples))
        """

def recorded_alarm_test():
    path = "data/audio/audio_1.wav"
    rate, data = AudioLoader.readWav(path)
    audio = AudioProcessor.resample(data, rate, 40000)
    audio = audio[:40000*5]
    #audio = audio[100000:150000]
    audio = Maths.normalize(audio, np.max(audio))

    lpf_filter = IIRFilter()
    hpf_filter = IIRFilter()
    final_stage_hpf = IIRFilter()

    coeffs = setup_zoll_coeffs()

    detector = AlarmDetector()
    filtered = []
    lpf = []
    hpf = []
    sig = []

    lpf_signal_slice = []
    hpf_signal_slice = []
    signal_slice = []
    alarm = []

    length = 40000 / 20

    # for entry in audio:
    #     filtered_low = lpf_filter.filter(entry, coeffs[0])
    #     #filtered_high = hpf_filter.filter(entry, coeffs[1])
    #
    #     filtered_signal = final_stage_hpf.filter(filtered_low, coeffs[1])
    #     filtered.append(filtered_signal)
    #
    #     detector.tick(filtered_signal)
    #     alarm.append(detector.alarm)

        # lpf_signal_slice.append(filtered_low)
        # if len(lpf_signal_slice) > length:
        #     lpf_signal_slice.pop(0)
        #
        # hpf_signal_slice.append(filtered_high)
        # if len(hpf_signal_slice) > length:
        #     hpf_signal_slice.pop(0)
        #
        # signal_slice.append(filtered_signal)
        # if len(signal_slice) > length:
        #     signal_slice.pop(0)

        #sig.append(np.std(detector.signal_slice))
        #lpf.append(np.std(lpf_signal_slice))
        #hpf.append(np.std(hpf_signal_slice))

    graph.plot_data(audio)
    # graph.plot_data(lpf, clear=False)
    # graph.plot_data(hpf, clear=False)
    # graph.plot_data(sig, clear=False)
    #graph.plot_data(alarm, clear=False)
    #graph.set_legend(["Audio", "Alarm"])
    #graph.set_legend(["Audio", "low_pass", "high_pass", "band_pass"])
    graph.save_plot("alarm_audio.png", xLabel="Sample", yLabel="Amplitude", title="Zoll Alarm Audio")

def mic_test():
    import wave
    from DSP import SignalReader
    reader = SignalReader()
    reader.setup()

    coeffs = setup_zoll_coeffs()
    lpf_filter = IIRFilter(coeffs[0])
    hpf_filter = IIRFilter(coeffs[1])
    final_stage_hpf = IIRFilter(coeffs[1])
    detector = AlarmDetector()

    tick = 0
    while True:
        tick += 1
        samples = reader.read(reader.sampling_rate*10, oversample_num=reader.sampling_rate//40000)
        print("RECEIVED",len(samples),"FROM READER")
        audio = np.divide(samples, np.max(samples))
        print(np.max(audio))

        filtered = []
        lpf = []
        hpf = []
        sig = []

        lpf_signal_slice = []
        hpf_signal_slice = []
        signal_slice = []
        alarm = []

        length = 40000 / 20
        print("filtering...")
        for entry in audio:

            filtered_low = lpf_filter.filter(entry)
            #filtered_high = hpf_filter.filter(entry)

            filtered_signal = final_stage_hpf.filter(filtered_low)
            filtered.append(filtered_signal)

            detector.tick(filtered_signal)
            alarm.append(detector.alarm)

            # lpf_signal_slice.append(filtered_low)
            # if len(lpf_signal_slice) > length:
            #     lpf_signal_slice.pop(0)
            #
            # hpf_signal_slice.append(filtered_high)
            # if len(hpf_signal_slice) > length:
            #     hpf_signal_slice.pop(0)
            #
            # signal_slice.append(filtered_signal)
            # if len(signal_slice) > length:
            #     signal_slice.pop(0)
            #
            # sig.append(np.std(detector.signal_slice))
            # lpf.append(np.std(lpf_signal_slice))
            # hpf.append(np.std(hpf_signal_slice))

            # if detector.get_alarm_status():
            #     print("!!ON!!")
            # else:
            #     print("!!OFF!!")

        # graph.plot_data(audio)
        # graph.plot_data(lpf, clear=False)
        # graph.plot_data(hpf, clear=False)
        # graph.plot_data(sig, clear=False)
        #graph.plot_data(alarm, clear=False)
        #graph.set_legend(["Audio", "Alarm"])
        #graph.set_legend(["Audio", "low_pass", "high_pass", "band_pass"])

        graph.plot_data(np.divide(filtered, np.max(filtered)))
        graph.plot_data(alarm,clear=False)
        graph.save_plot("test_{}.png".format(tick))
        print("done")

def test_2():
    from DSP import SDTest
    tester = SDTest.test()
    tester.start()

def process_test():
    coeffs = setup_zoll_coeffs()

    #This is dummy config json for testing purposes.
    cfg = {"sampling_rate":40000,
           "high_pass_coeffs":coeffs[1],
           "low_pass_coeffs":coeffs[0],
           "std_update_rate":40000//10,
           "alarm_detection_threshold":2,
           "alarm_report_period":0.2}

    #Set up the DSP process.
    process = OpenMonitorDSPProcess()
    handler = MPFProcessHandler()
    handler.setup_process(process)

    #Send the config off to the DSP process.
    handler.put(header=OpenMonitorDSPProcess.UPDATE_CONFIG_HEADER,data=cfg)

    import time

    #This loop checks the I/O queue from the DSP process for the current alarm status every so often.
    while True:
        time.sleep(cfg["alarm_report_period"])
        data = handler.get_all()
        if data is None:
            continue

        del data

def main():
    process_test()
    #mic_test()
    #test_2()

if __name__ == "__main__":
    main()