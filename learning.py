from binance_reader.analyzeHelpers import *
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
import numpy as np
import os
import learningHelper as LH


def rolling_window(a, window, step_size):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


if __name__ == '__main__':
    BASE_PATH = os.path.join("binance_reader", "clear_klines_data")
    symbol = "BTCUSDT"

    filenames = readFileNames(os.path.join(BASE_PATH, symbol))
    for filename in filenames:
        # Reading raw dataset
        print filename
        path = os.path.join(BASE_PATH, symbol, filename)
        raw_data = np.genfromtxt(path, delimiter=";")
        print "data.shape: ", raw_data.shape

        # Getting spesific feature from dataset
        features = [LH.OPEN, LH.HIGH, LH.LOW, LH.CLOSE, LH.BUY_BASE_VOLUME, LH.BUY_QUOTE_VOLUME]
        data = raw_data[:, features]

        step = 1
        open_returns = calculateReturns(data, step=step)
        open_returns = open_returns[:-step]

        window_size = 50
        label_step = 1
        data = rolling_window(open_returns, window_size, 1)

        data = data[:-label_step]
        labels = open_returns[window_size + label_step - 1: -1]

        print "data.shape: ", data.shape
        print "labels.shape: ", labels.shape

        nn = MLPRegressor(verbose=True, activation='tanh', solver='sgd',
                          hidden_layer_sizes=(100,))

        testCount = 50
        train_data = data[:-testCount]
        train_labels = labels[:-testCount]
        test_data = data[-testCount:]
        test_labels = labels[-testCount:]

        nn.fit(train_data, train_labels)
        predicts = nn.predict(test_data)
        print "predict and labels"
        print predicts[:5]
        print test_labels[:5]

        count = 0
        for i in range(len(predicts)):
            if predicts[i] > 0 and test_labels[i] > 0:
                count += 1
            elif predicts[i] < 0 and test_labels[i] < 0:
                count += 1
        print "total: ", len(predicts), " count: ", count

        mse = ((predicts - test_labels) ** 2).mean(axis=None)
        print "mse: ", mse

        x = range(len(test_labels))
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.scatter(x, test_labels, s=1, c='b', marker="s", label='real')
        ax1.scatter(x, predicts, s=10, c='r', marker="o", label='NN Prediction')
        plt.show()
