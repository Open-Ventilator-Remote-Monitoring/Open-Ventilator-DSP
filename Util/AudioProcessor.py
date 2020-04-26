import numpy as np
import scipy.signal
import numpy.fft as fft
import matplotlib
from Util import Maths
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def process_spectrogram(data,fs=8000):
    plt.clf()
    spec, time, freq, img = plt.specgram(data,Fs=fs)
    #print("before:",np.mean(spec),np.max(spec),np.min(spec))
    spec = np.where(spec==0, 1, spec)
    spec = -10*np.log10(spec)
    #spec = Maths.normalize(spec)
    #print("after:",np.mean(spec),np.max(spec),np.min(spec))

    return spec

def create_spectrogram(data,fs=8000):
    windowus = 50000
    stepus = 1000
    #
    print(len(data))

    step = int(max(1,stepus * fs / 1000000))
    window = int(max(1,windowus * fs / 1000000))
    steps = int(round((len(data) - window) / step))
    print("taking", steps, "steps")

    stft = []
    times = []
    freqs = []

    for i in range(steps):
        sample = data[step * i: step * i + window]
        n = 256
        if (n == 0):
            return 0

        # data - np.where(abs(data)<0.1, 0, data)
        dft = fft.fft(sample,n=n)
        dft = np.abs(dft)
        #dft = np.square(dft)
        freqs = []
        for j in range(len(dft)):
            freqs.append(j * fs / n)
        times.append(i/steps)

        freqs = freqs[:len(dft) // 2]
        #dft = np.fft.fftshift(dft)
        dft = dft[:len(dft) // 2]
        stft.append(dft)

    freqs = np.asarray(freqs)
    times = np.asarray(times)
    print(freqs.shape)
    print(times.shape)
    stft = np.asarray(stft).astype(np.float32)
    #stft = np.multiply(stft, np.power(2,20)-1)
    print(stft.shape)
    print(np.max(stft))
    return times, freqs, stft

    ###do blackman windowing

def process_entropy(data, fs=8000):
    '''
    A function to compute the entropy inside a window of audio.

    :param data: The audio to be processed.
    :param fs: The sampling rate of the audio being processed.
    :return: The entropy of the audio segment provided.
    '''

    n = len(data)
    if(n == 0):
        return 0

    #data - np.where(abs(data)<0.1, 0, data)
    dft = fft.fft(data)
    dft = np.abs(dft)

    dft = dft[:len(dft)//2]

    data = compute_entropy(dft)

    return data

def compute_entropy(dft):
    '''
    Function to compute the spectral entropy of a dft.

    :param dft: The positive spectral magnitude values from the fourier transform
    of some audio.

    :param freqs: The frequency components corresponding to the spectral magnitudes provided
    in the dft.

    :return: The entropy value of the dft.
    '''
    low = len(dft)*0
    high = len(dft)*0.75
    entropySignal = []
    entropy = 0
    dft = np.sort(dft)
    dft = np.square(dft)

    summation = np.sum(dft)

    if summation <= 0:
        return 0

    entropySignal = np.divide(dft, summation)


    for i in range(len(dft)):

        if i < high and i > low:
            continue
        else:
            entropySignal[i] = 0

    for i in range(len(dft)):
        if entropySignal[i] != 0:
            entropy -= entropySignal[i] * np.log(abs(entropySignal[i]))

    return entropy
def create_sample_list(audio, sampleTimems=1000, stepSizems = 10, fs=8000):
    '''
    Function to convert an audio waveform into a list of waveforms of length sampleTimeSec

    :param audio: The audio to be converted
    :param sampleTimeSec: The time length of each audio segment
    :param fs: The sampling rate of the audio
    :return: The list of audio segments
    '''

    samples = []
    window = int(round(sampleTimems*fs/1000))
    step = int(round(stepSizems*fs/1000))
    numSamples = int(round((len(audio) - window)/step))
    for i in range(numSamples):
        sample = audio[i*step : window + i*step]
        samples.append(sample)
    return samples

def process_list(samples, op = process_entropy, windowSizems = 100, timeStepms = 5, fs=8000, debug=False):
    '''
    Function to process a list of audio samples into a list of some other form of data.

    :param samples: The list of audio samples to be processed
    :param op: The operation to be used on each sample
    :param windowSizems: The size of the window to be operated on at each op call
    :param timeStepms: The amount of time to shift the window over at each iteration
    :param fs: The sampling rate of the audio provided in the sample list
    :param debug: Debug parameter to help development
    :return: An array of processed samples
    '''
    if debug:
        xAxes = []

    processedSamples = []
    for sample in samples:
        processedSubsamples = process_single_sample(sample,op=op,windowSizems=windowSizems,
                                                      timeStepms=timeStepms,fs=fs,debug=debug)
        if processedSubsamples is None:
            continue

        if debug:
            processedSubsamples, xAxis, _ = processedSubsamples
            xAxes.append(xAxis)
        processedSamples.append(processedSubsamples)


    if debug:
        return np.asarray(processedSamples), np.asarray(xAxes), np.asarray(samples)

    return processedSamples



def process_audio_in_place(audio,sampleTimeSec=1,op = process_entropy, windowSizems = 100, timeStepms = 5, fs=8000, debug=False):
    '''
    Alternative function to process_list, this is equivalent to the following:

    >> lst = create_sample_list(audio, sampleTimeSec, fs)
    >> return process_list(lst, op, windowSizems, timeStepms, fs, debug)

    The reason this function exists is to avoid the excess memory usage of creating a list of audio samples.
    Instead, this function will find each sample of size sampleTimeSec and process it immediately into an entropy list.

    :param audio: The audio to be converted
    :param sampleTimeSec: The time length of each audio segment
    :param op: The operation to be used on each sample
    :param windowSizems: The size of the window to be operated on at each op call
    :param timeStepms: The amount of time to shift the window over at each iteration
    :param fs: The sampling rate of the audio provided in the sample list
    :param debug: Debug parameter to help development
    :return: An array of processed samples
    '''


    counter = 0

    processedSamples = []

    audioStep = int(sampleTimeSec * fs)
    numSamples = int(len(audio) / audioStep)
    if debug:
        samples = []
        xAxes = []

    for i in range(numSamples):
        sample = audio[i * audioStep: audioStep + i * audioStep]
        counter = counter + 1

        processedSubsamples = process_single_sample(sample,op=op,windowSizems=windowSizems,
                                                    timeStepms=timeStepms,fs=fs,debug=debug)
        if processedSubsamples is None:
            continue

        if debug:
            processedSubsamples, xAxis, sample = processedSubsamples
            xAxes.append(xAxis)
            samples.append(sample)


        processedSamples.append(np.asarray(processedSubsamples))
    if debug:
        return np.asarray(processedSamples), np.asarray(xAxes), np.asarray(samples)
    return np.asarray(processedSamples)

def process_single_sample(sample, desiredSampleLength = None, op = process_entropy, windowSizems = 100, timeStepms = 5, fs=8000, debug=False):
    if desiredSampleLength is None:
        desiredSampleLength = fs

    if len(sample) != desiredSampleLength:
        print("INCORRECTLY SIZED SAMPLE!\nGot:",len(sample),"\nExpected:",desiredSampleLength)
        return None

    windowSize = fs * windowSizems // 1000
    step = fs * timeStepms // 1000
    steps = (len(sample) - windowSize) // step

    if steps <= 0:
        return None

    processedSubsamples = []

    if debug:
        xAxis = []
    for j in range(steps):
        begin = step * j
        end = min(len(sample) - 1, step * j + windowSize)

        subSample = sample[begin:end]
        processedSubsamples.append(op(subSample, fs=fs))
        if debug:
            xAxis.append(begin)

    if debug:
        return processedSubsamples, xAxis, sample

    return processedSubsamples
def resample(data, current, desired):
    '''
    Wrapper function to resample some audio from its current sampling rate to a desired sampling rate.
    This function is currently unnecessary, as one could just call scipy.signal.resample_poly(data,desired,current)
    without using this function. However, it may be necessary to implement a custom resampling method in the future,
    so the system is built to use this resampling function.

    :param data: Audio to be resampled
    :param current: Current sampling rate of the audio
    :param desired: Desired new sampling rate of the audio
    :return: Resampled audio
    '''
    return scipy.signal.resample_poly(data, desired, current)


def bandpass_filter(data, fl, fh, fs, order):
    '''
    Function to apply a bandpass filter to some signal.

    :param data: The signal to be filtered.
    :param fl: The low frequency band
    :param fh: The high frequency band
    :param fs: The sampling rate of the signal
    :param order: The order of bandpass filter to use
    :return: A filtered signal
    '''

    nyquist = fs/2
    b,a = scipy.signal.butter(order,[fl/nyquist, fh/nyquist],btype='band', output='ba')
    flter = scipy.signal.lfilter(b,a,data)
    return flter


