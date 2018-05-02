from binance_reader.analyzeHelpers import *
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
import numpy as np
import os
import learningHelper as LH
import learingMeta as LM

def rolling_window(a, window, step_size):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


if __name__ == '__main__':
    BASE_PATH = os.path.join("binance_reader", "clear_klines_data")
    symbol = "BTCUSDT"

    filenames = readFileNames(os.path.join(BASE_PATH, symbol))
    raw_datasets = []

    for filename in filenames:
        # Reading raw dataset
        path = os.path.join(BASE_PATH, symbol, filename)
        print "path: ", path
        raw_data = np.genfromtxt(path, delimiter=";")
        raw_datasets.append(raw_data)
    meta = LM.prepareMeta()

    dataset, headerList = LM.createDataFrame(raw_datasets, meta)
    LH.normalize_dataset(dataset)
