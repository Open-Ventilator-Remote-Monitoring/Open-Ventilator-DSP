import scipy.io.wavfile
import numpy as np
import os
from Util import Maths
from Util import AudioProcessor as proc


def readWav(fileName):
    print('READING',fileName)
    try:
        rate, data = scipy.io.wavfile.read(fileName)
    except:
        import wavio
        file = wavio.read(fileName)
        rate = file.rate
        data = file.data
    # print(data.shape)
    if len(data.shape) > 1:
        return rate, data[:, 0]
    return rate, data


def writeWav(data, rate, fileName, dtype=np.float32):
    stereo = np.asarray([data, data], dtype=dtype)
    print(stereo.shape, np.max(data), np.min(data), data.dtype)

    scipy.io.wavfile.write(fileName, rate, stereo.T)


def locate_samples(trainingDataDirectory):
    print("Locating samples...")
    noiseFolders = []
    voiceFolders = []
    for folder in os.listdir(trainingDataDirectory):
        print("Checking", folder)
        if os.path.isdir("{}/{}".format(trainingDataDirectory, folder)):
            print("Determined folder to be a directory")
            if "noise" in folder:
                noiseFolders.append(folder)
            elif "voice" in folder or "speech" in folder:
                voiceFolders.append(folder)

    voiceSampleList = []
    noiseSampleList = []

    for folder in noiseFolders:
        folderPath = "{}/{}".format(trainingDataDirectory, folder)

        for file in os.listdir(folderPath):
            if ".wav" not in file:
                continue

            noiseSampleList.append("{}/{}".format(folderPath, file))

    print("Found", len(noiseSampleList), "noise samples.")

    for folder in voiceFolders:
        folderPath = "{}/{}".format(trainingDataDirectory, folder)

        for file in os.listdir(folderPath):
            if ".wav" not in file:
                continue

            voiceSampleList.append("{}/{}".format(folderPath, file))

    print("Found", len(voiceSampleList), "voice samples.")

    return voiceSampleList, noiseSampleList, [voiceFolders, noiseFolders]


def load_audio_samples(trainingDataDirectory):
    voice = []
    noise = []
    voiceSampleList, noiseSampleList, _ = locate_samples(trainingDataDirectory)

    for location in voiceSampleList:
        print(location)

        sampleRate, audioFile = readWav(location)
        audioFile = force_legit_audio(audioFile, sampleRate)

        audioFile = np.float32(audioFile)
        voice.append(audioFile)

    for location in noiseSampleList:

        sampleRate, audioFile = readWav(location)
        audioFile = force_legit_audio(audioFile, sampleRate)

        audioFile = np.float32(audioFile)
        noise.append(audioFile)

    return voice, noise

def load_audio_samples_as_dict(trainingDataDirectory):
    voice = {}
    noise = {}
    voiceSampleList, noiseSampleList, _ = locate_samples(trainingDataDirectory)

    for location in voiceSampleList:
        print(location)

        sampleRate, audioFile = readWav(location)
        audioFile = force_legit_audio(audioFile, sampleRate)
        audioFile = np.float32(audioFile)

        name = location[location.rfind("/")+1 : location.rfind(".wav")]
        print(name)
        voice[name] = audioFile

    for location in noiseSampleList:
        sampleRate, audioFile = readWav(location)
        audioFile = force_legit_audio(audioFile, sampleRate)

        audioFile = np.float32(audioFile)
        name = location[location.rfind("/") + 1: location.rfind(".wav")]
        print(name)
        noise[name] = audioFile

    return voice, noise
def force_legit_audio(audioFile, sampleRate):
    if not (audioFile.dtype == np.float32 or audioFile.dtype == np.float64) \
            or max(abs(np.min(audioFile)), np.max(audioFile)) >= 2.0:
        print("NORMALIZING AUDIO FILE")
        audioFile = Maths.normalize(audioFile)

    if sampleRate != 8000:
        print("RESAMPLING AUDIO FILE FROM", sampleRate, "TO", 8000)
        audioFile = proc.resample(audioFile, sampleRate, 8000)

    return audioFile