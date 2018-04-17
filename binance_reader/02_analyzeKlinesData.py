from binance.client import Client
import binance.helpers
import pprint
import datetime
import os
import pytz
import timeit
from analyzeHelpers import *

if __name__ == '__main__':
    BASE_PATH = "klines_data"

    symbols = readFileNames(BASE_PATH)
    # symbols = ["BTCUSDT"]

    for symbol in symbols:
        print "symbol: ", symbol
        symbol_path = os.path.join(BASE_PATH, symbol)
        filenames = readFileNames(symbol_path)

        filesLst = getFilesMeta(BASE_PATH, symbol)

        findex = 0
        while filesLst[findex]["numberofline"] == 0:
            findex += 1

        filesLst = filesLst[findex:]

        corruptedLst = filter(lambda x: not x["usable"], filesLst)
        pprint.pprint(corruptedLst)
        print "firstFile: ", filesLst[0]["filename"]
        print "len(corruptedLst): ", len(corruptedLst)
        print "len(data): ", len(filesLst)
        print "*" * 30
        # checkRows(os.path.join(symbol_path, corruptedLst[4]["filename"]), debug=True)
