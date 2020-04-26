import numpy as np


def normalize(data, maxVal=None):
    # Check if data has already been normalized
    if maxVal is not None:
        return np.divide(data, maxVal)

    if np.max(data) <= 1.1 and np.min(data) >= -1.1:
        return data

    if maxVal is None:
        try:
            maxVal = np.iinfo(data.dtype).max
        except:
            try:
                maxVal = np.finfo(data.dtype).max
            except Exception as e:
                print(e)
    return np.divide(data, maxVal)

def smooth(data):
    test = np.where(data<0,0,data)
    num_samples = 2000
    for i in range(num_samples, len(data)):
        data[i] /= np.mean(test[i-num_samples:i])