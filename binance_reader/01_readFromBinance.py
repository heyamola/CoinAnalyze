from binance.client import Client

import pprint
import datetime
import os
import timeit
import urllib2
import json
from analyzeHelpers import *

if __name__ == '__main__':
    BASE_PATH = "klines_data"
    ALL_SYMBOLS = None

    def getSymbolNames(cur1="", cur2=""):
        global ALL_SYMBOLS
        if not ALL_SYMBOLS:
            url = "https://www.binance.com/api/v1/ticker/allPrices"
            req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
            resp = urllib2.urlopen(req, timeout=30)
            ALL_SYMBOLS = json.load(resp)

        symbols = map(lambda x: x["symbol"], ALL_SYMBOLS)
        if cur1:
            symbols = filter(lambda x: x.startswith(cur1.upper()), symbols)
        if cur2:
            symbols = filter(lambda x: x.endswith(cur2.upper()), symbols)
        return symbols

    def process_message(msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something

    def getDayStr(min):
        return (datetime.datetime.utcnow() - datetime.timedelta(minutes=min)).isoformat()

    def createSymbolFolder(symbol):
        path = os.path.join(BASE_PATH, symbol)
        print "symbol path: ", path
        if os.path.exists(path):
            print "directory already exists."
            return path

        print "Creating directory..."
        os.makedirs(path)
        return path

    client = Client("a", "a")
    interval = datetime.timedelta(minutes=24 * 60)
    deltaTime = datetime.timedelta(seconds=1)
    now = datetime.datetime.utcnow()

    # symbols = []
    # symbols += getSymbolNames(cur2="usdt")
    # symbols += getSymbolNames(cur1="ltc")
    # symbols += getSymbolNames(cur2="ltc")
    # symbols += getSymbolNames(cur1="XRP")
    # symbols += getSymbolNames(cur2="XRP")
    # symbols += getSymbolNames(cur1="eth")
    # symbols += getSymbolNames(cur2="eth")
    # symbols = symbols[:60]
    symbols = readFileNames("klines_data")

    print "len(symbols)", len(symbols)
    # exit(1)

    for i, symbol in enumerate(symbols):
        print "symbol: ", symbol,  "(%s/%s)" % (i + 1, len(symbols))
        symbol_directory = createSymbolFolder(symbol)

        start_day = datetime.datetime.strptime("2017-08-01", "%Y-%m-%d")
        while (start_day + interval) < now:
            start_date_str = start_day.isoformat()
            end_date_str = (start_day + interval - deltaTime).isoformat()
            start_day += interval

            print "symbol: ", symbol,  "(%s/%s)" % (i + 1, len(symbols)), \
                "---", "start_date_str: ", start_date_str, \
                "--- end_date_str: ", end_date_str

            filename = "{}.csv".format(start_date_str)
            filePath = os.path.join(symbol_directory, filename)
            if os.path.exists(filePath):
                print "day already fetched. \n"
                continue

            print "fetching..."
            start = timeit.default_timer()
            klines = client.get_historical_klines(symbol,
                                                  Client.KLINE_INTERVAL_1MINUTE,
                                                  start_date_str,
                                                  end_date_str)
            end = timeit.default_timer()
            print "fetch time: ", end - start
            print "writing to file... len(klines): ", len(klines)
            fileObj = open(filePath, "wb")
            for row in klines:
                row = map(lambda x: str(x), row)
                fileObj.write(";".join(row))
                fileObj.write("\n")
            print "done\n"
