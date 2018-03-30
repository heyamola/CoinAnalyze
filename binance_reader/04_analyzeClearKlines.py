from analyzeHelpers import *
from learningHelper import *
import os
from pprint import pprint
import csv

def analyzePair(pairPath, step=5):
    pairName = os.path.basename(pairPath)
    dataFiles = readFileNames(pairPath)

    allData = None
    allReturns = np.array([])
    for dataFile in dataFiles:
        dataFilePath = os.path.join(pairPath, dataFile)
        data = readFile(dataFilePath)
        print "data.shape: ", data.shape

        if type(allData) == type(None):
            allData = np.copy(data)
        else:
            allData = np.append(allData, data, axis=0)

        returns = calculateReturns(data, CLOSE[0], step=step)
        returns *= 100
        allReturns = np.append(allReturns, returns)

    print "allData.shape: ", allData.shape
    result = analyzeReturns(allReturns, 0)
    result.update({"pair": pairName,
                   "numberofinput": allReturns.shape[0],
                   "step(min)": step,
                   "trade_avg" : allData[:, NUMBER_OF_TRADE[0]].mean(),
                   "trade_std" : allData[:, NUMBER_OF_TRADE[0]].std(),
                   "volume_avg": allData[:, VOLUME[0]].mean(),
                   "volume_std": allData[:, VOLUME[0]].std(),
                   })

    return result


if __name__ == '__main__':
    BASE_PATH = "clear_klines_data"
    pairs = readFileNames(BASE_PATH)

    outPutFile = "pairAnalyze.csv"
    header = ["pair", "min", "max", "mean", "std", "rf", "trade_avg", "trade_std",
              "volume_avg", "volume_std", "numberofinput", "sharpratio", "step(min)"]

    pairResults = [dict(zip(header, header))]
    for index, pair in enumerate(pairs):
        print "pair: %s  --- (%02d/%02d)" % (pair, index + 1, len(pairs))
        pairPath = os.path.join(BASE_PATH, pair)
        result = analyzePair(pairPath, step=5)
        pprint(result)
        pairResults.append(result)

    saveToCSV(outPutFile, pairResults, header)




