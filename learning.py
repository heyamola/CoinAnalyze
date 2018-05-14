from binance_reader.analyzeHelpers import *
from sklearn.neural_network import MLPRegressor, MLPClassifier
import matplotlib.pyplot as plt
import numpy as np
import os
import learningHelper as LH
import learingMeta as LM
import labelCreator as LC
import time


def saveNumpyToFile(arr, filename, header=None):
    DEBUG_PATH = "DEBUG_FILES/"
    header_str = ";".join(header)
    np.savetxt("%s%s" % (DEBUG_PATH, filename), arr, header=header_str, delimiter=";")


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

    dataFrames, headerList = LM.createDataFrames(raw_datasets, meta)

    datasets = []
    window_size = 30
    for i, dataFrame in enumerate(dataFrames):
        print "dataFrame: %02d" % i
        dataset, labels = dataFrame[:, :-1], dataFrame[:, -1]
        splitLabels = LC.labelSplitter(labels)

        LH.normalize_dataset(dataset)
        dataset = LH.rolling_window(dataset, window_size)
        splitLabels = splitLabels[window_size - 1:, :]

        print "splittedLabels.shape: ", splitLabels.shape
        print "dataset.shape: ", dataset.shape

        datasets.append((dataset, splitLabels))
        time.sleep(0.5)

    print "concatenate data..."
    trainingData = np.concatenate(map(lambda x: x[0], datasets[:-1]))
    trainingLabels = np.concatenate(map(lambda x: x[1], datasets[:-1]))
    testData = datasets[-1][0]
    testLabel = datasets[-1][1]

    print "MLPClassifier..."
    clf = MLPClassifier(hidden_layer_sizes=5, activation="relu", solver="adam", learning_rate="adaptive",
                        verbose=True, max_iter=50)
    clf.fit(trainingData, trainingLabels)

    score = clf.score(testData, testLabel)
    predicts = clf.predict_proba(testData)
    predicts_binary = map(lambda x: 0 if x[0] > x[1] else 1, predicts)

    for i in range(100):
        print "prediction: %s --- real: %s" % (predicts[i], testLabel[i])

    print "predict 0/1: %d/%d" % (predicts_binary.count(0), predicts_binary.count(1))
    print "real 0/1: %d/%d" % (list(testLabel[:, 0]).count(1), list(testLabel[:, 1]).count(1))
    print "score: ", score
